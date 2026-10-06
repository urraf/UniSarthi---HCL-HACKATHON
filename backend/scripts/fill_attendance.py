"""
Synthetic attendance for every (student, course) that has a result but no attendance row,
so every student can ask about attendance in all their courses.

Consistent with the result: DETAINED -> below the 60% floor; otherwise 78-96%.
Seeded, so running it again gives the same rows. Existing rows (the hand-placed edge cases) are kept.

Run:  python scripts/fill_attendance.py && python scripts/validate_data.py --dir data/students
"""
import csv
import random
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "students"


def main() -> None:
    random.seed(20261006)
    att_file = DATA / "attendance.csv"
    with att_file.open(newline="") as f:
        reader = csv.DictReader(f)
        cols, rows = reader.fieldnames, list(reader)
    have = {(r["student_id"], r["course_code"]) for r in rows}

    # latest result per (student, course)
    latest = {}
    with (DATA / "results.csv").open(newline="") as f:
        for r in csv.DictReader(f):
            latest[(r["student_id"], r["course_code"])] = r["result"]

    added = 0
    for (sid, course), result in sorted(latest.items()):
        if (sid, course) in have:
            continue
        held = random.randint(38, 45)
        pct = random.uniform(0.50, 0.58) if result == "DETAINED" else random.uniform(0.78, 0.96)
        rows.append({"student_id": sid, "course_code": course, "classes_held": held,
                     "classes_attended": int(held * pct)})
        added += 1

    with att_file.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Added {added} attendance rows ({len(rows)} total)")


if __name__ == "__main__":
    main()
