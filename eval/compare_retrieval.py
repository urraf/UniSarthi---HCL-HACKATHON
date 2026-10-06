"""
Compare two embedding models and two top-k values on RETRIEVAL only (no LLM needed).

For every eval question that has an expected source, we check whether that document
is among the top-k chunks returned by ChromaDB.
  - hit@k:  expected chunk found in the top k
  - MRR:    1 / rank of the expected chunk (higher = it ranks nearer the top)

The chunks are copied from the main collection into one collection per model,
so both models see exactly the same text.

Run (from backend/):  python ../eval/compare_retrieval.py
Writes eval/retrieval_comparison.md
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "backend"))
from app import config, vectors  # noqa: E402

MODELS = ["sentence-transformers/all-MiniLM-L6-v2", "BAAI/bge-small-en-v1.5"]
K_VALUES = [3, 5]


def main() -> None:
    questions = [q for q in json.loads((HERE / "questions.json").read_text()) if q.get("expected_doc")]
    source = vectors.collection().get()  # all chunks of the main collection

    rows = []
    for model in MODELS:
        coll = vectors.collection(model)
        if coll.count() != len(source["ids"]):  # (re)build this model's copy of the chunks
            if coll.count():
                coll.delete(ids=coll.get()["ids"])
            coll.add(ids=source["ids"], documents=source["documents"], metadatas=source["metadatas"])

        ranks = []
        for q in questions:
            hits = vectors.search(q["question"], k=max(K_VALUES), coll=coll)
            found = [i + 1 for i, h in enumerate(hits) if h["doc_id"] == q["expected_doc"]]
            ranks.append(found[0] if found else None)

        row = {"model": model}
        for k in K_VALUES:
            row[f"hit@{k}"] = sum(1 for r in ranks if r and r <= k) / len(ranks)
        row["MRR"] = sum(1 / r for r in ranks if r) / len(ranks)
        rows.append(row)
        print(row)

    lines = ["# Retrieval comparison", "",
             f"{len(questions)} eval questions with an expected document. Same chunks for both models.", "",
             "| Embedding model | " + " | ".join(f"hit@{k}" for k in K_VALUES) + " | MRR |",
             "|---|" + "---|" * (len(K_VALUES) + 1),
             *[f"| {r['model']} | " + " | ".join(f"{r[f'hit@{k}']:.0%}" for k in K_VALUES) + f" | {r['MRR']:.2f} |" for r in rows],
             "", f"Configured model (EMBED_MODEL): {config.EMBED_MODEL}, TOP_K={config.TOP_K}"]
    (HERE / "retrieval_comparison.md").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
