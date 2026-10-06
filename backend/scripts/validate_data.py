"""
Validate student CSV files against the guide's schema (Annex C) and logic rules.

Checks:
  - required columns exist
  - student_id format S#### and judges' reserved IDs (S9000-S9999) / JDG courses not used
    (only when checking OUR data; judges' own files use those IDs on purpose)
  - ranges: semester 1-10, CGPA 0-10, backlogs >= 0
  - attendance: held > 0 and 0 <= attended <= held
  - marks: total = internal + external, total <= max, result consistent with marks
  - active_backlogs equals the number of non-PASS results
  - every course's programme matches the student's programme
  - required edge cases are present (only for our generated data)

Thresholds (pass mark, attendance, CGPA cut-off) are read from rules_seed.csv, not typed in code.

Run:  python scripts/validate_data.py                 (our data in data/students)
      python scripts/validate_data.py --dir some/dir  (any folder with the 4 CSVs)
"""
import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config  # noqa: E402

REQUIRED_COLUMNS = {
    "students.csv": ["student_id", "full_name", "programme", "batch_year", "current_semester", "cgpa", "active_backlogs"],
    "courses.csv": ["course_code", "course_name", "programme", "semester", "credits"],
    "attendance.csv": ["student_id", "course_code", "classes_held", "classes_attended"],
    "results.csv": ["student_id", "course_code", "exam_session", "exam_type", "internal_marks",
                    "external_marks", "total_marks", "max_marks", "result"],
}


def read_csv(path: Path) -> list[dict]:
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def rule_values(parameter: str) -> list[float]:
    """All values a parameter has in the rule registry seed (e.g. 75 and 80 for attendance)."""
    with open(config.DATA_DIR / "rules_seed.csv") as f:
        return [float(r["value"]) for r in csv.DictReader(f) if r["parameter"] == parameter]


def validate(folder: Path, our_data: bool = True) -> tuple[list[str], list[str]]:
    """Return (violations, edge_case_report). No violations means the data is valid."""
    errors: list[str] = []

    # 1. Files and columns
    tables = {}
    for name, cols in REQUIRED_COLUMNS.items():
        path = folder / name
        if not path.exists():
            errors.append(f"missing file {name}")
            continue
        rows = read_csv(path)
        missing = [c for c in cols if rows and c not in rows[0]]
        if missing:
            errors.append(f"{name}: missing columns {missing}")
        tables[name] = rows
    if errors:
        return errors, []

    students = {s["student_id"]: s for s in tables["students.csv"]}
    courses = {c["course_code"]: c for c in tables["courses.csv"]}
    pass_pct = rule_values("pass_marks_pct")[0]

    # 2. Students
    for sid, s in students.items():
        if not re.fullmatch(r"S\d{4}", sid):
            errors.append(f"{sid}: student_id must be S followed by 4 digits")
        if our_data and 9000 <= int(sid[1:] or 0) <= 9999:
            errors.append(f"{sid}: IDs S9000-S9999 are reserved for judges")
        if not 1 <= int(s["current_semester"]) <= 10:
            errors.append(f"{sid}: current_semester out of range")
        if not 0 <= float(s["cgpa"]) <= 10:
            errors.append(f"{sid}: cgpa out of range")
        if int(s["active_backlogs"]) < 0:
            errors.append(f"{sid}: active_backlogs negative")

    for code in courses:
        if our_data and code.startswith("JDG"):
            errors.append(f"{code}: course codes starting with JDG are reserved for judges")

    # 3. Attendance
    for a in tables["attendance.csv"]:
        key = f"{a['student_id']} {a['course_code']}"
        held, attended = int(a["classes_held"]), int(a["classes_attended"])
        if a["student_id"] not in students:
            errors.append(f"{key}: unknown student")
        if a["course_code"] not in courses:
            errors.append(f"{key}: unknown course")
        elif a["student_id"] in students and courses[a["course_code"]]["programme"] != students[a["student_id"]]["programme"]:
            errors.append(f"{key}: course programme does not match student programme")
        if held <= 0:
            errors.append(f"{key}: classes_held must be > 0")
        if not 0 <= attended <= held:
            errors.append(f"{key}: classes_attended must be between 0 and classes_held")

    # 4. Results
    backlogs: dict[str, int] = {sid: 0 for sid in students}
    for r in tables["results.csv"]:
        key = f"{r['student_id']} {r['course_code']}"
        internal, external = int(r["internal_marks"]), int(r["external_marks"])
        total, max_marks = int(r["total_marks"]), int(r["max_marks"])
        if total != internal + external:
            errors.append(f"{key}: total_marks {total} != internal + external ({internal + external})")
        if total > max_marks:
            errors.append(f"{key}: total_marks above max_marks")
        if r["result"] not in ("PASS", "FAIL", "ABSENT", "DETAINED"):
            errors.append(f"{key}: invalid result {r['result']}")
        if r["exam_type"] not in ("REGULAR", "SUPPLEMENTARY"):
            errors.append(f"{key}: invalid exam_type {r['exam_type']}")
        pass_mark = pass_pct * max_marks / 100
        if r["result"] == "PASS" and total < pass_mark:
            errors.append(f"{key}: PASS but total {total} is below pass mark {pass_mark:g}")
        if r["result"] == "FAIL" and total >= pass_mark:
            errors.append(f"{key}: FAIL but total {total} reaches pass mark {pass_mark:g}")
        if r["result"] in ("ABSENT", "DETAINED") and external != 0:
            errors.append(f"{key}: {r['result']} must have external_marks 0")
        if r["result"] != "PASS" and r["student_id"] in backlogs:
            backlogs[r["student_id"]] += 1

    for sid, count in backlogs.items():
        if int(students[sid]["active_backlogs"]) != count:
            errors.append(f"{sid}: active_backlogs {students[sid]['active_backlogs']} but {count} non-PASS results")

    report = edge_case_report(students, tables, pass_pct) if our_data else []
    errors += [line for line in report if line.startswith("MISSING")]
    return errors, report


def edge_case_report(students: dict, tables: dict, pass_pct: float) -> list[str]:
    """Confirm the guide's required edge cases exist, and name the students that carry them."""
    att_thresholds = rule_values("min_attendance_pct")
    cgpa_cutoffs = rule_values("placement_min_cgpa")
    att = tables["attendance.csv"]
    res = tables["results.csv"]

    def pct(a):
        return 100 * int(a["classes_attended"]) / int(a["classes_held"])

    def one_class_below(a, t):
        held, attended = int(a["classes_held"]), int(a["classes_attended"])
        return pct(a) < t and 100 * (attended + 1) / held >= t

    checks = {
        "attendance exactly at a threshold": [f"{a['student_id']} {a['course_code']}" for a in att if any(abs(pct(a) - t) < 1e-9 for t in att_thresholds)],
        "attendance one class below a threshold": [f"{a['student_id']} {a['course_code']}" for a in att if any(one_class_below(a, t) for t in att_thresholds)],
        "failed with marks just below pass": [f"{r['student_id']} {r['course_code']}" for r in res if r["result"] == "FAIL" and int(r["total_marks"]) == int(pass_pct * int(r["max_marks"]) / 100) - 1],
        "absent result": [f"{r['student_id']} {r['course_code']}" for r in res if r["result"] == "ABSENT"],
        "detained student": [f"{r['student_id']} {r['course_code']}" for r in res if r["result"] == "DETAINED"],
        "multiple backlogs": [sid for sid, s in students.items() if int(s["active_backlogs"]) >= 2],
        "CGPA exactly at placement cut-off": [sid for sid, s in students.items() if float(s["cgpa"]) in cgpa_cutoffs],
    }
    return [f"{'OK     ' if found else 'MISSING'} {name}: {', '.join(found) or '-'}" for name, found in checks.items()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", default=str(config.DATA_DIR / "students"))
    parser.add_argument("--external", action="store_true", help="judges' data: skip reserved-ID and edge-case checks")
    args = parser.parse_args()

    errors, report = validate(Path(args.dir), our_data=not args.external)
    lines = ["Edge cases:", *report, "", f"Violations: {len(errors)}", *errors]
    print("\n".join(lines))
    if not args.external:
        (Path(args.dir) / "validation_report.txt").write_text("\n".join(lines) + "\n")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
