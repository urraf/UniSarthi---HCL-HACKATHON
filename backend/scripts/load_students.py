"""
Load student CSV files (Annex C schema) into SQLite.
Judges use this to load their own test students.

Run:  python scripts/load_students.py                       (our generated data)
      python scripts/load_students.py --dir test_students/  (judges' data)

The files are validated first. Rows are inserted or replaced (upsert),
so running it twice is safe. Students then create their own account (sign up with email OTP).
"""
import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config, db  # noqa: E402
from scripts.validate_data import load_dir, validate  # noqa: E402

TABLES = ["courses", "students", "attendance", "results"]  # parents first (foreign keys)
ALIASES = {"roll_no": "roll_number"}                          # CSV column -> our column


def table_columns(conn, table: str) -> list[str]:
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]


def load_folder(folder: Path) -> dict:
    """Validate and load the CSV files. Only columns that exist in our tables are loaded."""
    errors, _stats = validate(load_dir(folder))
    if errors:
        print("Validation failed, nothing loaded:")
        print("\n".join(f"  - {e}" for e in errors))
        raise SystemExit(1)

    db.init_db()
    counts = {}
    with db.connect() as conn:
        for table in TABLES:
            with open(folder / f"{table}.csv", newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                known = set(table_columns(conn, table))
                pairs = [(c, ALIASES.get(c, c)) for c in reader.fieldnames if ALIASES.get(c, c) in known]
                # empty cells (e.g. marks of an ABSENT result) become NULL
                rows = [[(row[src] if row[src] != "" else None) for src, _ in pairs] for row in reader]
            cols = [dst for _, dst in pairs]
            conn.executemany(f"INSERT OR REPLACE INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)})", rows)
            counts[table] = len(rows)
    return counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=str(config.DATA_DIR / "students"))
    args = parser.parse_args()
    print(f"Loaded: {load_folder(Path(args.dir))}")


if __name__ == "__main__":
    main()
