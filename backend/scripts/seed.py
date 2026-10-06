"""
Build the whole database from the files in data/ (safe to run again).

  1. create tables
  2. source register  (data/source_register.csv)  -> documents table
  3. rule registry    (data/rules_seed.csv)       -> rule_registry table
  4. students         (data/students/*.csv)       -> student tables + logins

Run:  python scripts/seed.py
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config, db  # noqa: E402
from scripts.create_logins import create_missing_logins  # noqa: E402
from scripts.load_students import load_folder  # noqa: E402

DOC_COLUMNS = ["doc_id", "title", "issuer", "authority_level", "doc_type", "version", "effective_from",
               "effective_to", "supersedes", "scope_programmes", "scope_batches", "provenance",
               "retrieved_on", "synthetic", "file_name"]
RULE_COLUMNS = ["rule_id", "description", "parameter", "operator", "value", "scope_programmes",
                "scope_batches", "effective_from", "effective_to", "source_doc_id", "source_section"]


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def upsert(table: str, columns: list[str], rows: list[dict]) -> None:
    placeholders = ", ".join("?" for _ in columns)
    with db.connect() as conn:
        conn.executemany(
            f"INSERT OR REPLACE INTO {table} ({', '.join(columns)}) VALUES ({placeholders})",
            [[row[c] for c in columns] for row in rows],
        )


def load_source_register() -> list[dict]:
    rows = read_csv(config.DATA_DIR / "source_register.csv")
    upsert("documents", DOC_COLUMNS, rows)
    return rows


def load_rules() -> int:
    """Every rule must point to a document in the source register (guide, Annex C)."""
    rules = read_csv(config.DATA_DIR / "rules_seed.csv")
    known_docs = {d["doc_id"] for d in db.query("SELECT doc_id FROM documents")}
    for r in rules:
        if r["source_doc_id"] not in known_docs:
            raise SystemExit(f"Rule {r['rule_id']} cites unknown document {r['source_doc_id']}")
    upsert("rule_registry", RULE_COLUMNS, rules)
    return len(rules)


def main() -> None:
    db.init_db()
    docs = load_source_register()
    print(f"Documents registered: {len(docs)}")
    print(f"Rules loaded: {load_rules()}")
    print(f"Students loaded: {load_folder(config.DATA_DIR / 'students', our_data=True)}")
    print(f"Logins created: {create_missing_logins()}")


if __name__ == "__main__":
    main()
