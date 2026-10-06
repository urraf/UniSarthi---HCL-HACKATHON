# Retrieval comparison

12 eval questions with an expected document + section. Same chunks for both models.

| Embedding model | hit@3 | hit@5 | MRR |
|---|---|---|---|
| sentence-transformers/all-MiniLM-L6-v2 | 100% | 100% | 0.74 |
| BAAI/bge-small-en-v1.5 | 92% | 92% | 0.72 |

Configured model (EMBED_MODEL): BAAI/bge-small-en-v1.5, TOP_K=5
