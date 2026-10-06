"""
ChromaDB: stores document chunks and finds the ones closest in meaning to a question.

- Persisted to disk (data/chroma), so documents are NOT re-ingested on every restart.
- Embeddings come from a sentence-transformers model (EMBED_MODEL in .env).
- Each chunk keeps its document metadata (doc_id, section, page, version, dates, authority...)
  so we can filter by date/scope and build citations without asking the LLM.
"""
import re

import chromadb
from chromadb.config import Settings
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

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
        embedding_function=SentenceTransformerEmbeddingFunction(model_name=model_name),
        metadata={"hnsw:space": "cosine"},  # cosine distance: similarity = 1 - distance
    )
    if model_name == config.EMBED_MODEL:
        _collection = coll
    return coll


def count_chunks(doc_id: str) -> int:
    return len(collection().get(where={"doc_id": doc_id})["ids"])


def delete_doc(doc_id: str) -> None:
    collection().delete(where={"doc_id": doc_id})


def add_chunks(doc_id: str, chunks: list[dict], coll=None) -> None:
    """chunks: [{"text": ..., "metadata": {...}}]. Chroma metadata values cannot be None."""
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
