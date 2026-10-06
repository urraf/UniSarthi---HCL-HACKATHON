"""Quick retrieval check: python scripts/query_chroma.py "your question" [-k 4]"""
import argparse, sys
sys.path.insert(0, __import__("os").path.dirname(__file__))
import ingest

ap = argparse.ArgumentParser()
ap.add_argument("question")
ap.add_argument("-k", type=int, default=4)
a = ap.parse_args()
col = ingest.get_collection()
emb = ingest.get_model().encode([a.question], normalize_embeddings=True).tolist()
r = col.query(query_embeddings=emb, n_results=a.k)
for d, m, dist in zip(r["documents"][0], r["metadatas"][0], r["distances"][0]):
    print(f"[{1 - dist:.2f}] {m['doc_id']} v{m['version']} eff {m['effective_from']} p.{m['page']} sec '{m['section']}' ocr={m['ocr']}")
    print("   ", d[:260].replace("\n", " "))
