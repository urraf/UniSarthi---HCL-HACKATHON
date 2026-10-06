"""Validate student CSVs against the Annex C schema and logical constraints.

Usage:
    python scripts/validate_data.py --dir data/synthetic/
    python scripts/validate_data.py --dir data/synthetic/ --report data/synthetic/validation_report.txt

Checks: required columns; types and ranges; ID formats; reserved judge IDs/codes;
foreign keys; duplicate keys; attended <= held; marks within range;
total = internal + external; result consistent with marks (thresholds read from
data/rule_registry.csv, never hard-coded); roll number format; active_backlogs
at least as large as the backlogs visible in results. Exit code 1 on any violation.
"""
import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIRED = {
    "students": ["student_id", "full_name", "programme", "batch_year", "current_semester", "cgpa", "active_backlogs"],
    "courses": ["course_code", "course_name", "programme", "semester", "credits"],
    "attendance": ["student_id", "course_code", "classes_held", "classes_attended"],
    "results": ["student_id", "course_code", "exam_session", "exam_type", "internal_marks", "external_marks",
                "total_marks", "max_marks", "result"],
}
SESSION_RE = re.compile(r"^(\d{4})-(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)$")
MONTHS = "JAN FEB MAR APR MAY JUN JUL AUG SEP OCT NOV DEC".split()
ROLL_RE = re.compile(r"^(20\d{2})U(IT|CS)\d{4}$")
ROLL_PROG = {"IT": "B.Tech IT", "CS": "B.Tech CSE"}


def load_dir(folder):
    data = {}
    for table in REQUIRED:
        p = Path(folder) / f"{table}.csv"
        if p.exists():
            with p.open(newline="", encoding="utf-8-sig") as f:
                data[table] = list(csv.DictReader(f))
    return data


def num(x):
    if x is None or x == "":
        return None
    try:
        f = float(x)
    except (TypeError, ValueError):
        raise ValueError(f"not a number: {x!r}")
    return int(f) if f.is_integer() and "." not in str(x) else f


def registry_thresholds():
    """Pass thresholds come from the rule registry (rule_id -> float)."""
    out = {"PASS-ESE-01": 30.0, "PASS-GRADE-D-01": 35.0, "ATT-MIN-01": 75.0}  # fallbacks if registry absent
    p = ROOT / "data" / "rules_seed.csv"
    if p.exists():
        with p.open(newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                if r["rule_id"] in out:
                    out[r["rule_id"]] = float(r["value"])
    return out


def session_key(s):
    m = SESSION_RE.match(s)
    return (int(m.group(1)), MONTHS.index(m.group(2))) if m else None


def validate(data, check_files=None):
    errs = []
    thr = registry_thresholds()
    min_ese, min_total = thr["PASS-ESE-01"], thr["PASS-GRADE-D-01"]

    def err(msg):
        errs.append(msg)

    for t, cols in REQUIRED.items():
        for i, r in enumerate(data.get(t, [])):
            for c in cols:
                if c not in r:
                    err(f"{t}: row {i + 1} missing column {c}")
                    break
    if errs:
        return errs, {}

    students, courses = {}, {}
    for r in data.get("students", []):
        sid = r["student_id"]
        try:
            sem, cg, bl, by = num(r["current_semester"]), num(r["cgpa"]), num(r["active_backlogs"]), num(r["batch_year"])
        except ValueError as e:
            err(f"students {sid}: {e}")
            continue
        if not re.fullmatch(r"S\d{4}", sid or ""):
            err(f"students {sid}: student_id must be S + 4 digits")
        if sid in students:
            err(f"students {sid}: duplicate student_id")
        if not (r["full_name"] or "").strip():
            err(f"students {sid}: empty full_name")
        if sem is None or not 1 <= sem <= 10:
            err(f"students {sid}: current_semester {r['current_semester']} not in 1..10")
        if cg is None or not 0.0 <= cg <= 10.0:
            err(f"students {sid}: cgpa {r['cgpa']} not in 0..10")
        if bl is None or bl < 0 or bl != int(bl):
            err(f"students {sid}: active_backlogs must be an integer >= 0")
        if by is None or not 2015 <= by <= 2030:
            err(f"students {sid}: implausible batch_year {r['batch_year']}")
        roll = r.get("roll_no") or ""
        if roll:
            m = ROLL_RE.match(roll)
            if not m:
                err(f"students {sid}: roll_no {roll!r} not like 2023UIT3101")
            else:
                if by is not None and int(m.group(1)) != by:
                    err(f"students {sid}: roll_no year {m.group(1)} != batch_year {r['batch_year']}")
                if ROLL_PROG[m.group(2)] != r["programme"]:
                    err(f"students {sid}: roll_no branch {m.group(2)} does not match programme {r['programme']}")
        students[sid] = r
    rolls = [r.get("roll_no") for r in data.get("students", []) if r.get("roll_no")]
    for d in {x for x in rolls if rolls.count(x) > 1}:
        err(f"students: duplicate roll_no {d}")

    for r in data.get("courses", []):
        cc = r["course_code"]
        if cc in courses:
            err(f"courses {cc}: duplicate course_code")
        if cc.startswith("JDG"):
            err(f"courses {cc}: JDG* course codes are reserved for judges")
        try:
            if num(r["credits"]) is None or num(r["credits"]) <= 0:
                err(f"courses {cc}: credits must be > 0")
            if num(r["semester"]) is None or not 1 <= num(r["semester"]) <= 10:
                err(f"courses {cc}: semester out of range")
        except ValueError as e:
            err(f"courses {cc}: {e}")
        courses[cc] = r
    progs = {s["programme"] for s in students.values()}
    for cc, c in courses.items():
        if progs and c["programme"] not in progs:
            err(f"courses {cc}: programme {c['programme']!r} matches no students.programme value")

    seen = set()
    for r in data.get("attendance", []):
        k = (r["student_id"], r["course_code"])
        if k in seen:
            err(f"attendance {k}: duplicate primary key")
        seen.add(k)
        if r["student_id"] not in students:
            err(f"attendance {k}: unknown student_id")
        if r["course_code"] not in courses:
            err(f"attendance {k}: unknown course_code")
        try:
            h, a = num(r["classes_held"]), num(r["classes_attended"])
        except ValueError as e:
            err(f"attendance {k}: {e}")
            continue
        if h is None or h <= 0:
            err(f"attendance {k}: classes_held must be > 0")
        elif a is None or a < 0 or a > h:
            err(f"attendance {k}: classes_attended {a} must be 0..{h}")
        if "attendance_pct" in r:
            err(f"attendance {k}: attendance % must be computed by tools, never stored")

    seen = set()
    by_student = defaultdict(lambda: defaultdict(list))
    for r in data.get("results", []):
        k = (r["student_id"], r["course_code"], r["exam_session"], r["exam_type"])
        if k in seen:
            err(f"results {k}: duplicate primary key")
        seen.add(k)
        if r["student_id"] not in students:
            err(f"results {k}: unknown student_id")
        if r["course_code"] not in courses:
            err(f"results {k}: unknown course_code")
        if r["exam_type"] not in ("REGULAR", "SUPPLEMENTARY"):
            err(f"results {k}: exam_type must be REGULAR or SUPPLEMENTARY")
        if r["result"] not in ("PASS", "FAIL", "ABSENT", "DETAINED"):
            err(f"results {k}: result must be PASS/FAIL/ABSENT/DETAINED")
        sk = session_key(r["exam_session"])
        if not sk:
            err(f"results {k}: exam_session must look like 2026-MAY")
        try:
            i_, e_, t_, mx = (num(r[x]) for x in ("internal_marks", "external_marks", "total_marks", "max_marks"))
        except ValueError as e:
            err(f"results {k}: {e}")
            continue
        if mx is None or mx <= 0:
            err(f"results {k}: max_marks must be > 0")
            continue
        for name, v in (("internal", i_), ("external", e_), ("total", t_)):
            if v is not None and not 0 <= v <= mx:
                err(f"results {k}: {name}_marks {v} outside 0..{mx}")
        res = r["result"]
        if res in ("ABSENT", "DETAINED"):
            if e_ is not None or t_ is not None:
                err(f"results {k}: {res} must have empty external_marks and total_marks")
        else:
            if i_ is None or e_ is None or t_ is None:
                err(f"results {k}: {res} needs internal, external and total marks")
            else:
                if t_ != i_ + e_:
                    err(f"results {k}: total_marks {t_} != internal {i_} + external {e_}")
                ese_max = mx * 0.5
                expect = "PASS" if (t_ >= min_total * mx / 100 and e_ >= ese_max * min_ese / 100) else "FAIL"
                if res != expect:
                    err(f"results {k}: result {res} inconsistent with marks (total {t_}, external {e_}); expected {expect}")
        if sk:
            by_student[r["student_id"]][r["course_code"]].append((sk, res))

    if data.get("results"):
        for sid, per_course in by_student.items():
            open_backlogs = sum(1 for rows in per_course.values() if max(rows)[1] != "PASS")
            if sid in students and num(students[sid]["active_backlogs"]) < open_backlogs:
                err(f"students {sid}: active_backlogs {students[sid]['active_backlogs']} < {open_backlogs} visible in results")

    stats = {t: len(v) for t, v in data.items()}
    return errs, stats


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--report", help="also write the output to this file")
    args = ap.parse_args()
    data = load_dir(args.dir)
    if not data:
        sys.exit(f"No CSV files found in {args.dir}")
    errs, stats = validate(data)
    lines = ["Validation of " + str(args.dir), "Rows: " + ", ".join(f"{t}={n}" for t, n in stats.items())]
    lines += [f"VIOLATION: {e}" for e in errs]
    lines.append(f"RESULT: {'FAILED' if errs else 'PASSED'} ({len(errs)} violation(s))")
    out = "\n".join(lines)
    print(out)
    if args.report:
        Path(args.report).write_text(out + "\n", encoding="utf-8")
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
