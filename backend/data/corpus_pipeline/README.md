# Corpus preparation pipeline

The code that produced `backend/data/chunks/nsut_chunks.jsonl`, `source_register.csv` and the rule registry from the
24 NSUT documents in `backend/data/docs/`. It was developed in the team data repo
[anish295/HCL-Database](https://github.com/anish295/HCL-Database) and is included here so the corpus can be rebuilt and
explained.

| File | What it does |
|---|---|
| `build_registers.py` | Builds the Source Register (Annex B) and rule registry; every rule must cite a registered document. `KEEP` lists the corpus scope: standing policies + notices dated 2026. |
| `ingest.py` | Extracts text per page (PyMuPDF; RapidOCR for scanned pages; openpyxl for the .xlsx), splits into clause-aware chunks (~900 chars, 150 overlap, never across a page), embeds with `all-MiniLM-L6-v2`, stores in ChromaDB with Annex B metadata plus `page`, `section`, `clauses`, `ocr`. |
| `query_chroma.py` | Quick retrieval check from the command line. |

Paths: these scripts expect the data repo layout (`data/documents`, `data/source_register.csv`, `data/chroma`). To run
them here, point `DOCS`, `REGISTER` and `CHROMA_DIR` at `backend/data/...` or run them inside the data repo.
Requirements: `chromadb`, `sentence-transformers`, `rapidocr-onnxruntime`, `openpyxl`, `pymupdf`.
Scanned pages (`ocr=Y`) can contain OCR errors; check the scan before quoting exact figures.
