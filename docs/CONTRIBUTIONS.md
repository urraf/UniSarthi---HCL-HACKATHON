# Team contribution statement

Every member owns the files below, pushes them from their own GitHub account, and can explain them line by line. Everyone must also be able to explain the whole flow (`backend/app/pipeline/graph.py`) and the precedence policy (`backend/app/precedence.py`), because judges ask about parts you did not build.

## Farhan: frontend + backend API + guard/finalize steps + Docker

| Files | What it is |
|---|---|
| `frontend/` (all) | React app: login / sign up / forgot password / staff login, student chat with history, staff document upload and sources |
| `backend/app/main.py` | FastAPI endpoints `/ask /ingest /health /audit /sources /login /me` |
| `backend/app/schemas.py` | Pydantic request/response models (the API contract) |
| `backend/app/auth.py`, `backend/app/account_routes.py`, `backend/app/mongo.py`, `backend/app/mailer.py`, `backend/scripts/create_logins.py`, `backend/scripts/create_admin.py`, `backend/tests/test_auth.py` | Accounts in MongoDB: roll-number login, sign up / forgot password with email OTP, forgot roll number, staff login, chat history |
| `backend/app/config.py` | All settings from `.env` |
| `backend/app/pipeline/guard.py` | Step 1: who is asking, refuse other students' data |
| `backend/app/pipeline/finalize.py` | Final step: answer_type, citations, audit record |
| `backend/tests/test_guard.py` | Privacy tests |
| `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`, `.env.example`, `.gitignore`, `backend/requirements.txt`, `README.md` | Setup and packaging |

## Manish: Python tools + SQL schema + calling them from LangGraph

| Files | What it is |
|---|---|
| `backend/app/db.py` | SQLite schema (Annex C tables + documents, logins, audit) and helpers |
| `backend/app/tools.py` | 7 deterministic tools: attendance, results, exam / supplementary / placement eligibility, what-if |
| `backend/app/precedence.py` | Source Precedence Policy (Annex A) in code |
| `backend/data/rules_seed.csv` | Rule registry: every threshold with its document and clause |
| `backend/app/pipeline/calculate.py` | Step 4: which tools run for which intent (fixed plans) |
| `backend/scripts/load_students.py` | Loader for judges' CSV files |
| `backend/tests/conftest.py`, `test_tools.py`, `test_precedence.py` | Tests incl. the guide's worked example |

## Nikita: LangGraph + LLM interaction + LLM-generated data

| Files | What it is |
|---|---|
| `backend/app/llm.py` | One helper for Groq / Ollama / mock, JSON mode, retries, token counting |
| `backend/app/pipeline/state.py` | Shared state and the list of intents |
| `backend/app/pipeline/graph.py` | LangGraph wiring: steps, branches, stop-to-finalize |
| `backend/app/pipeline/understand.py` | Step 2: LLM labels the question (+ keyword fallback) |
| `backend/app/pipeline/answer.py` | Step 5: LLM writes the answer from evidence only |
| `backend/scripts/generate_students.py`, `backend/scripts/validate_data.py`, `backend/data/prompts/`, `backend/data/students/`, `backend/data/team_schema.sql` | Synthetic student data kit and SQL schema (from the team data repo) |
| `docs/DATA_CARD.md` | Synthetic data card |

## Anish: sources + ChromaDB embeddings + find step + evaluation

| Files | What it is |
|---|---|
| `backend/data/docs/`, `backend/data/source_register.csv`, `backend/data/POLICY_INDEX.md`, `backend/data/chunks/nsut_chunks.jsonl`, `backend/data/rules_seed.csv` | Collected the 24 NSUT documents, Source Register, rule registry, OCR + clause-aware chunking and embeddings (team repo anish295/HCL-Database) |
| `backend/app/vectors.py` | ChromaDB: persisted collection, embeddings, search |
| `backend/app/ingest.py` | Parse PDF/MD/TXT, split by section, injection filter, embed, rule extraction for live documents |
| `backend/scripts/seed.py` | Builds everything from `data/` (skips documents already indexed) |
| `backend/app/pipeline/find.py` | Step 3: search, date/scope filter, supersession, ranking, citations |
| `eval/` (all) | 29-question evaluation set, `run_eval.py`, `compare_retrieval.py`, reports |
| `docs/AI_USAGE.md` | AI usage disclosure |

## Push order (so the project works after every push)

1. **Farhan**: setup files (`.gitignore`, `.env.example`, `backend/requirements.txt`, `backend/app/__init__.py`, `backend/app/config.py`, `README.md`)
2. **Manish**: `db.py`, `tools.py`, `precedence.py`, `rules_seed.csv`, `load_students.py`, `scripts/__init__.py`, tests
3. **Nikita**: `llm.py`, data kit (`generate_students.py`, `validate_data.py`, `prompts/`, `students/`), `DATA_CARD.md`
4. **Anish**: documents, `source_register.csv`, `vectors.py`, `ingest.py`, `seed.py`, `pipeline/find.py`
5. **Nikita**: `pipeline/__init__.py`, `state.py`, `understand.py`, `answer.py`, `graph.py`
6. **Manish**: `pipeline/calculate.py`
7. **Farhan**: `auth.py`, `create_logins.py`, `schemas.py`, `main.py`, `pipeline/guard.py`, `pipeline/finalize.py`, `test_guard.py`, `frontend/`, Docker files
8. **Anish**: `eval/`, `AI_USAGE.md`
9. **Farhan**: final README, tag `final`

Note: `load_students.py` imports `create_logins.py` and `graph.py` imports every step, so a few intermediate pushes only fully run once the later files arrive. That is expected.
