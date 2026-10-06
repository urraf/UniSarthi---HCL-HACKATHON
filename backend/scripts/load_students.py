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
from scripts.validate_data import validate  # noqa: E402

# table name -> columns, in the order of the Annex C schema
TABLES = {
    "students": ["student_id", "full_name", "programme", "batch_year", "current_semester", "cgpa", "active_backlogs"],
    "courses": ["course_code", "course_name", "programme", "semester", "credits"],
    "attendance": ["student_id", "course_code", "classes_held", "classes_attended"],
    "results": ["student_id", "course_code", "exam_session", "exam_type", "internal_marks",
                "external_marks", "total_marks", "max_marks", "result"],
}


def load_folder(folder: Path, our_data: bool) -> dict:
    """Validate and load the 4 CSV files. Returns row counts per table."""
    errors, _ = validate(folder, our_data=our_data)
    if errors:
        print("Validation failed, nothing loaded:")
        print("\n".join(f"  - {e}" for e in errors))
        raise SystemExit(1)

    db.init_db()
    counts = {}
    with db.connect() as conn:
        # courses and students first, because attendance/results point to them
        for table, cols in TABLES.items():
            with open(folder / f"{table}.csv", newline="") as f:
                reader = csv.DictReader(f)
                # Optional extra column: roll_number (our data has it, judges' Annex C files may not)
                if table == "students" and "roll_number" in (reader.fieldnames or []):
                    cols = cols + ["roll_number"]
                rows = [[row[c] for c in cols] for row in reader]
            placeholders = ", ".join("?" for _ in cols)
            conn.executemany(f"INSERT OR REPLACE INTO {table} ({', '.join(cols)}) VALUES ({placeholders})", rows)
            counts[table] = len(rows)
    return counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=str(config.DATA_DIR / "students"))
    args = parser.parse_args()

    folder = Path(args.dir)
    our_data = folder.resolve() == (config.DATA_DIR / "students").resolve()
    counts = load_folder(folder, our_data)
    print(f"Loaded: {counts}")


if __name__ == "__main__":
    main()
