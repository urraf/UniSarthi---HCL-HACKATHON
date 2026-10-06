# UniSarthi: AI-Powered University Student Services Assistant

HCLTech Future Ready AI Engineer Hackathon, team of 4.

A student asks a question. UniSarthi finds the rule in university documents, checks the student's own records with plain code, and answers with the source cited. If it cannot find the answer, it says so.

## Build phases

| Phase | What | Owner |
|---|---|---|
| 1 | Project setup, SQLite schema, synthetic student data kit, logins | Member 3 (data) + Member 1 (setup) |
| 2 | Rule registry, precedence policy, deterministic tools, tests | Member 3 |
| 3 | Documents: parse, chunk, embed into ChromaDB, live `/ingest` | Member 2 |
| 4 | LangGraph pipeline + FastAPI endpoints + authentication + audit | Member 1 |
| 5 | React frontend | Member 4 |
| 6 | Evaluation, Docker, final docs | Member 4 + all |

## Phase 1: setup and data

```bash
cd backend
uv venv --python 3.11 .venv          # or: python3.11 -m venv .venv
uv pip install --python .venv/bin/python -r requirements.txt
cp ../.env.example .env               # then fill in the values

python scripts/generate_students.py   # LLM writes synthetic students (data/students/*.csv)
python scripts/validate_data.py       # checks schema, logic and edge cases
python scripts/load_students.py       # loads CSVs into SQLite + creates logins
```

Judges' data: `python scripts/load_students.py --dir path/to/test_students/`
