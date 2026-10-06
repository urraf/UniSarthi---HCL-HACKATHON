"""
ChromaDB: stores document chunks and finds the ones closest in meaning to a question.

- Persisted to disk (data/chroma), so documents are NOT re-ingested on every restart.
- Embeddings come from a sentence-transformers model (EMBED_MODEL in .env).
- Each chunk keeps its document metadata (doc_id, section, page, version, dates, authority...)
  so we can filter by date/scope and build citations without asking the LLM.
"""
import math
import re
from collections import Counter

import chromadb
from chromadb.config import Settings

from app import config

_collection = None


def collection(model_name: str | None = None):
    """Open (once) the Chroma collection for the chosen embedding model."""
    global _collection
    model_name = model_name or config.EMBED_MODEL
    if _collection is not None and model_name == config.EMBED_MODEL:
        return _collection

    client = chromadb.PersistentClient(path=str(config.CHROMA_DIR), settings=Settings(anonymized_telemetry=False))
    # One collection per embedding model, so switching models never mixes vectors
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", model_name.split("/")[-1]).strip("-").lower()
    coll = client.get_or_create_collection(
        name=f"docs-{slug}",
        embedding_function=_embedding_function(model_name),
        metadata={"hnsw:space": "cosine"},  # cosine distance: similarity = 1 - distance
    )
    if model_name == config.EMBED_MODEL:
        _collection = coll
    return coll


_keyword_index = None  # BM25 index over all chunks, rebuilt when documents change


def _embedding_function(model_name: str):
    """PyTorch sentence-transformers, or ChromaDB's ONNX copy of all-MiniLM-L6-v2 (same model, far less memory)."""
    import importlib.util
    # Use ONNX when asked, or automatically when PyTorch/sentence-transformers is not installed (e.g. on Render)
    if config.EMBED_BACKEND == "onnx" or importlib.util.find_spec("sentence_transformers") is None:
        if not model_name.endswith("all-MiniLM-L6-v2"):
            raise ValueError("EMBED_BACKEND=onnx only supports sentence-transformers/all-MiniLM-L6-v2")
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2
        # Plain CPU engine: other ONNX engines (e.g. CoreML on a Mac) use several hundred MB more memory
        return ONNXMiniLM_L6_V2(preferred_providers=["CPUExecutionProvider"])
    from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
    return SentenceTransformerEmbeddingFunction(model_name=model_name)


def count_chunks(doc_id: str) -> int:
    return len(collection().get(where={"doc_id": doc_id})["ids"])


def delete_doc(doc_id: str) -> None:
    global _keyword_index
    collection().delete(where={"doc_id": doc_id})
    _keyword_index = None


def add_chunks(doc_id: str, chunks: list[dict], coll=None) -> None:
    """chunks: [{"text": ..., "metadata": {...}}]. Chroma metadata values cannot be None."""
    global _keyword_index
    _keyword_index = None
    coll = coll or collection()
    coll.add(
        ids=[f"{doc_id}::{i}" for i in range(len(chunks))],
        documents=[c["text"] for c in chunks],
        metadatas=[{k: ("" if v is None else v) for k, v in c["metadata"].items()} for c in chunks],
    )


def search(question: str, k: int, coll=None) -> list[dict]:
    """Return the k closest chunks: [{"id", "text", "similarity", **metadata}]"""
    coll = coll or collection()
    if coll.count() == 0:
        return []
    res = coll.query(query_texts=[question], n_results=min(k, coll.count()))
    hits = []
    for chunk_id, text, meta, dist in zip(res["ids"][0], res["documents"][0], res["metadatas"][0], res["distances"][0]):
        hits.append({"id": chunk_id, "text": text, "similarity": round(1 - dist, 3), **meta})
    return hits


# ---------- Hybrid search: meaning (vectors) + exact words (BM25) ----------
STOPWORDS = set("""a an the is are was were be been of in on at to for from by with and or not no what which who whom
how when where why do does did i me my we our you your it its this that these those there can could should would will
shall may might must have has had about tell please give any all""".split())


def _tokens(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS and len(w) > 1]


def _build_keyword_index() -> dict:
    data = collection().get(include=["documents", "metadatas"])
    docs = [Counter(_tokens(t)) for t in data["documents"]]
    df = Counter(w for d in docs for w in d)
    return {"ids": data["ids"], "texts": data["documents"], "metas": data["metadatas"], "docs": docs,
            "lengths": [sum(d.values()) for d in docs], "df": df,
            "avg_len": sum(sum(d.values()) for d in docs) / max(len(docs), 1)}


def keyword_search(question: str, k: int) -> list[tuple[int, float]]:
    """BM25: (chunk position, score) for the k chunks sharing the most informative words with the question."""
    global _keyword_index
    if _keyword_index is None:
        _keyword_index = _build_keyword_index()
    idx, n = _keyword_index, len(_keyword_index["ids"])
    terms = set(_tokens(question))
    scores = []
    for i, doc in enumerate(idx["docs"]):
        score = 0.0
        for t in terms:
            if t in doc:
                idf = math.log(1 + (n - idx["df"][t] + 0.5) / (idx["df"][t] + 0.5))
                tf = doc[t]
                score += idf * tf * 2.2 / (tf + 1.2 * (0.25 + 0.75 * idx["lengths"][i] / idx["avg_len"]))
        if score > 0:
            scores.append((i, score))
    return sorted(scores, key=lambda x: -x[1])[:k]


def hybrid_search(question: str, k: int) -> list[dict]:
    """
    Vector hits and keyword hits merged by reciprocal rank fusion (a chunk ranked high by either wins).
    Every hit keeps its real cosine similarity (used for the "not found" threshold) and its keyword rank.
    """
    coll = collection()
    if coll.count() == 0:
        return []
    vector_hits = search(question, k * 3)
    keyword_hits = keyword_search(question, k * 3)
    fused, hits = {}, {h["id"]: h for h in vector_hits}
    for rank, h in enumerate(vector_hits):
        fused[h["id"]] = fused.get(h["id"], 0) + 1 / (60 + rank)
    idx = _keyword_index
    missing = []
    for rank, (i, _score) in enumerate(keyword_hits):
        cid = idx["ids"][i]
        fused[cid] = fused.get(cid, 0) + 1 / (60 + rank)
        if cid not in hits:
            missing.append(i)
        hits.setdefault(cid, {"id": cid, "text": idx["texts"][i], **idx["metas"][i]})["keyword_rank"] = rank + 1

    # Cosine similarity for keyword-only hits (so the relevance threshold still applies to them)
    if missing:
        ids = [idx["ids"][i] for i in missing]
        stored = coll.get(ids=ids, include=["embeddings"])
        q = coll._embedding_function([question])[0]
        qn = math.sqrt(sum(x * x for x in q))
        for cid, emb in zip(stored["ids"], stored["embeddings"]):
            en = math.sqrt(sum(x * x for x in emb))
            hits[cid]["similarity"] = round(sum(a * b for a, b in zip(q, emb)) / (qn * en), 3)

    ranked = sorted(fused, key=lambda cid: -fused[cid])[:k]
    return [hits[cid] for cid in ranked]
