# AI usage disclosure

The guide allows and encourages AI coding assistants, as long as we disclose how we used them and can explain every line.

## AI coding assistant

We used **Claude (Anthropic) in Claude Code** to help design the architecture and write a first version of the code, the sample documents, the evaluation questions and the documentation.

How we verified it:
- Every module has a test or an evaluation question that exercises it: `pytest` (24 tests: precedence policy incl. the guide's worked example, tools incl. every edge case, privacy guard) and `eval/run_eval.py` (29 questions against the live API).
- We ran every endpoint by hand (curl and the React UI): `/ask`, `/ingest` with an unseen document, `/audit`, `/sources`, `/health`, `/login`.
- Bugs found while verifying and fixed: chunks were ranked by authority before relevance (lost the FAQ answer), the what-if counted a DETAINED course as clearable, general questions with "I" were labelled personal, an injected instruction survived partially, and LLM rate limits (429) caused silent fallbacks.
- Each team member reviewed and can explain the files listed under their name in `CONTRIBUTIONS.md`.

## LLMs inside the system

| Where | Model | What it does |
|---|---|---|
| Answering questions (`pipeline/understand.py`, `pipeline/answer.py`) | Groq `qwen/qwen3.8-27b` (cloud), switchable to Ollama `qwen2.5:7b-instruct` (local) with `LLM_PROVIDER` | Labels the question, rewrites it for search; writes the answer from given evidence and tool results |
| Rule extraction on live ingest (`ingest.py`) | same | Proposes rule rows; kept only if the value appears verbatim in the cited section |
| Synthetic students (`scripts/generate_students.py`) | Claude in Claude Code wrote the seeded generator; rows come from the script | See `docs/DATA_CARD.md` |

**Cloud LLM disclosure (guide section 5):** the default `LLM_PROVIDER=groq` uses a cloud model. Setting `LLM_PROVIDER=ollama` in `backend/.env` switches to the local Ollama model with no code change. No real student data exists in the system, so no personal data is sent to the cloud.

## Reused code

No code was copied from other projects. Open-source libraries used: FastAPI, Pydantic, LangGraph, ChromaDB, sentence-transformers, pypdf, requests, React, Vite.
