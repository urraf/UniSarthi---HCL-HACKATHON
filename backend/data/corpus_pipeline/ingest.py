"""Chunk the NSUT documents, embed them and store them in a persistent ChromaDB.

Usage:
    python scripts/ingest.py                 # ingest every document in data/source_register.csv not yet in Chroma
    python scripts/ingest.py --force         # re-ingest everything
    python scripts/ingest.py --doc DEAN-SUMMER-2026

Pipeline per document:  extract text per page (PyMuPDF; RapidOCR for scanned pages; openpyxl for .xlsx)
-> clause-aware chunking (~900 chars, 150 overlap, never crosses a page) -> embeddings
(sentence-transformers all-MiniLM-L6-v2) -> Chroma collection `nsut_docs` (cosine) with the Annex B
metadata on every chunk, so retrieval can cite source/section/page/version/effective date and apply
the precedence policy. `ingest_file()` is reusable by a POST /ingest endpoint (R11, no restart needed).
"""
import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "data" / "documents"
REGISTER = ROOT / "data" / "source_register.csv"
CHROMA_DIR = ROOT / "data" / "chroma"
COLLECTION = "nsut_docs"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_CHARS, OVERLAP = 900, 150
OCR_MIN_CHARS = 60          # a page with less text than this is treated as scanned

_ocr = None
_model = None

# A clause/section heading at the start of a line: "11.2.", "12.3 ", "(a)", "Table 5", "Annexure A", "Section 4"
HEAD_RE = re.compile(r"^\s*((?:\d{1,2}(?:\.\d{1,2}){1,3}[.)]?\s)|(?:\d{1,2}\.\s+(?=[A-Z]))|(?:Table\s+\d+)|(?:Annex(?:ure)?\s+[A-Z0-9]+)|(?:Clause\s+\d+(?:\.\d+)*)|(?:Section\s+\d+))")


def get_ocr():
    global _ocr
    if _ocr is None:
        from rapidocr_onnxruntime import RapidOCR
        _ocr = RapidOCR()
    return _ocr


def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def ocr_image(png_bytes):
    result, _ = get_ocr()(png_bytes)
    if not result:
        return ""
    # result: [box, text, score]; sort by top-left y then x, group into lines by y proximity
    items = sorted(((b[0][1], b[0][0], t) for b, t, _ in result), key=lambda x: (round(x[0] / 12), x[1]))
    lines, cur, last_y = [], [], None
    for y, x, t in items:
        if last_y is not None and abs(y - last_y) > 12:
            lines.append(" ".join(cur))
            cur = []
        cur.append(t)
        last_y = y
    if cur:
        lines.append(" ".join(cur))
    return "\n".join(lines)


def extract_pages(path):
    """Yield (page_no, text, was_ocr)."""
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        import pymupdf
        doc = pymupdf.open(path)
        for i, page in enumerate(doc):
            text = page.get_text().strip()
            if len(text) >= OCR_MIN_CHARS:
                yield i + 1, text, False
            else:
                png = page.get_pixmap(dpi=200).tobytes("png")
                yield i + 1, ocr_image(png), True
    elif suffix in (".jpg", ".jpeg", ".png"):
        yield 1, ocr_image(path.read_bytes()), True
    elif suffix == ".xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        for ws in wb.worksheets:
            rows = [" | ".join(str(c) for c in row if c is not None) for row in ws.iter_rows(values_only=True)]
            rows = [r for r in rows if r.strip()]
            for k in range(0, len(rows), 25):          # 25 rows per "page" so each chunk stays small
                yield f"{ws.title}!{k + 1}", "\n".join(rows[k:k + 25]), False
    else:
        raise ValueError(f"unsupported file type {suffix}")


def clean(text):
    text = text.replace(" ", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_page(text):
    """Split a page into clause-aware chunks: break before clause headings, then pack to ~CHUNK_CHARS."""
    paras, cur = [], []
    for line in text.split("\n"):
        if HEAD_RE.match(line) and cur:
            paras.append("\n".join(cur))
            cur = []
        cur.append(line)
    if cur:
        paras.append("\n".join(cur))
    chunks, buf = [], ""
    for p in paras:
        p = p.strip()
        if not p:
            continue
        if len(p) > CHUNK_CHARS * 1.5:                       # very long paragraph: hard-split at sentence/space
            if buf:
                chunks.append(buf)
                buf = ""
            start = 0
            while start < len(p):
                end = min(len(p), start + CHUNK_CHARS)
                if end < len(p):
                    cut = max(p.rfind(". ", start, end), p.rfind(" ", start, end))
                    end = cut + 1 if cut > start + CHUNK_CHARS // 2 else end
                chunks.append(p[start:end].strip())
                start = max(end - OVERLAP, start + 1) if end < len(p) else end
        elif len(buf) + len(p) + 1 <= CHUNK_CHARS:
            buf = (buf + "\n" + p).strip()
        else:
            chunks.append(buf)
            tail = buf[-OVERLAP:] if OVERLAP and buf else ""
            buf = (tail + "\n" + p).strip() if tail else p
    if buf:
        chunks.append(buf)
    return [c for c in chunks if len(c) >= 25]


def clauses_in(chunk):
    """All clause/section headings found at line starts inside the chunk, in order (deduplicated)."""
    out = []
    for line in chunk.split("\n"):
        m = HEAD_RE.match(line)
        if m:
            c = re.sub(r"\s+", " ", m.group(1)).strip(" .)")
            if c not in out:
                out.append(c)
    return out


def load_register():
    with REGISTER.open(newline="", encoding="utf-8") as f:
        return {r["doc_id"]: r for r in csv.DictReader(f)}


def get_collection(client=None):
    import chromadb
    client = client or chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})


def ingest_file(path, meta, collection=None, replace=True):
    """Chunk + embed one file with its Annex B metadata dict. Returns number of chunks indexed."""
    collection = collection or get_collection()
    path = Path(path)
    doc_id = meta["doc_id"]
    if replace:
        collection.delete(where={"doc_id": doc_id})
    ids, docs, metas = [], [], []
    for page_no, raw, was_ocr in extract_pages(path):
        for n, chunk in enumerate(split_page(clean(raw))):
            ids.append(f"{doc_id}::p{page_no}::c{n}")
            docs.append(chunk)
            metas.append({
                "doc_id": doc_id, "title": meta["title"], "issuer": meta["issuer"],
                "authority_level": int(meta["authority_level"]), "doc_type": meta["doc_type"],
                "version": meta["version"], "effective_from": meta["effective_from"],
                "effective_to": meta.get("effective_to", "") or "", "supersedes": meta.get("supersedes", "") or "",
                "scope_programmes": meta["scope_programmes"], "scope_batches": meta["scope_batches"],
                "synthetic": meta.get("synthetic", "N"), "file_name": path.name,
                "page": str(page_no), "section": (clauses_in(chunk) or [""])[0],
                "clauses": ", ".join(clauses_in(chunk)[:12]), "ocr": "Y" if was_ocr else "N",
            })
    if not docs:
        return 0
    embeddings = get_model().encode(docs, batch_size=32, normalize_embeddings=True, show_progress_bar=False).tolist()
    collection.add(ids=ids, documents=docs, metadatas=metas, embeddings=embeddings)
    return len(docs)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--force", action="store_true", help="re-ingest documents already in Chroma")
    ap.add_argument("--doc", help="only this doc_id")
    args = ap.parse_args()
    register = load_register()
    col = get_collection()
    existing = {m["doc_id"] for m in col.get(include=["metadatas"])["metadatas"]} if col.count() else set()
    total = 0
    for doc_id, meta in register.items():
        if args.doc and doc_id != args.doc:
            continue
        if doc_id in existing and not args.force:
            print(f"skip   {doc_id} (already indexed)")
            continue
        path = DOCS / meta["file_name"]
        n = ingest_file(path, meta, col)
        total += n
        print(f"ingest {doc_id:28s} {n:4d} chunks  ({meta['file_name']})", flush=True)
    print(f"done: {total} chunks added; collection now has {col.count()} chunks")


if __name__ == "__main__":
    sys.exit(main())
