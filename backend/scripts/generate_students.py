"""Generate the synthetic student dataset (Annex C schema) into data/synthetic/.

Deterministic (seeded). 32 students, 2 programmes (B.Tech IT, B.Tech CSE), 2 batches
(2023, 2024), 10 real NSUT NEP course codes. All names/roll numbers are fabricated.
Edge cases are placed deliberately and listed in EDGE_CASES (also written to
data/synthetic/edge_cases.csv for the data card).

Run:  python scripts/generate_students.py && python scripts/validate_data.py --dir data/synthetic
"""
import csv
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "data" / "students"
random.seed(20261006)

IT, CSE = "B.Tech IT", "B.Tech CSE"
# Course codes/names are real NSUT NEP codes (from the 2025-26 Course Coordination Committee lists).
# Credits are NOT printed in any collected document; 4 is the full-course credit in Regulations-2019 Cl. 6.8.
COURSES = [
    ("ITITC302", "Database Management Systems", IT, 3, 4, "Theory"),
    ("ITITC304", "Advance Programming", IT, 3, 4, "Theory"),
    ("ITITC501", "Theory of Computation", IT, 5, 4, "Theory"),
    ("ITITC503", "Artificial Intelligence", IT, 5, 4, "Theory"),
    ("ITITC504", "Mobile Computing", IT, 5, 4, "Theory"),
    ("COCSC302", "Database Management Systems", CSE, 3, 4, "Theory"),
    ("COCSC303", "Design and Analysis of Algorithms", CSE, 3, 4, "Theory"),
    ("COCSC501", "Computer Networks", CSE, 5, 4, "Theory"),
    ("COCSC503", "Soft Computing", CSE, 5, 4, "Theory"),
    ("COCSC504", "Information and Data Security", CSE, 5, 4, "Theory"),
]
SEM3 = {IT: ["ITITC302", "ITITC304"], CSE: ["COCSC302", "COCSC303"]}
SEM5 = {IT: ["ITITC501", "ITITC503", "ITITC504"], CSE: ["COCSC501", "COCSC503", "COCSC504"]}

FIRST = ["Aarav", "Vihaan", "Reyansh", "Ishaan", "Kabir", "Arnav", "Dhruv", "Yash", "Tanvi", "Ananya", "Diya", "Meera",
         "Saanvi", "Kavya", "Riya", "Navya", "Harsh", "Pranav", "Lakshya", "Siddharth", "Nikhil", "Rahul", "Aditya",
         "Mohit", "Ritika", "Shreya", "Pooja", "Neha", "Tushar", "Varun", "Jatin", "Kritika"]
LAST = ["Sharma", "Verma", "Gupta", "Mehta", "Kapoor", "Malhotra", "Bansal", "Chauhan", "Joshi", "Nair", "Iyer", "Reddy",
        "Das", "Bose", "Khanna", "Saxena", "Tiwari", "Yadav", "Rawat", "Bhatia", "Arora", "Sethi", "Taneja", "Grover",
        "Dahiya", "Rana", "Tomar", "Pandey", "Mishra", "Sinha", "Ahuja", "Walia"]
random.shuffle(FIRST)
random.shuffle(LAST)

# (student_id, programme, batch). 8 per programme-batch -> 32 students.
ROSTER = []
sid = 1001
for prog, batch in [(IT, 2023), (IT, 2024), (CSE, 2023), (CSE, 2024)]:
    for _ in range(8):
        ROSTER.append((f"S{sid}", prog, batch))
        sid += 1

# ---- Edge cases: per student, explicit overrides. -------------------------------------------------------
# att[course] = (held, attended); res[(course, session, type)] = (internal, external) | "ABSENT" | "DETAINED"
EDGE = {
    "S1001": dict(cgpa=8.50, note="CGPA exactly 8.50 (B.Tech Honours cut-off, Cl. 7.9/15.4); all courses passed"),
    "S1002": dict(cgpa=6.90, att={"ITITC501": (40, 30)},
                  res={("ITITC501", "2025-DEC", "REGULAR"): (14, 20)},
                  note="Fail one mark below pass (total 34 < 35); re-registered with attendance exactly 75% (30/40)"),
    "S1003": dict(cgpa=6.40, att={"ITITC503": (40, 29)},
                  res={("ITITC503", "2025-DEC", "REGULAR"): "ABSENT"},
                  note="ABSENT result; re-registered with attendance one class below 75% (29/40 = 72.5%)"),
    "S1004": dict(cgpa=5.00, att={"ITITC504": (40, 24), "ITITC503": (40, 26)}, extra_backlogs=1,
                  res={("ITITC504", "2025-DEC", "REGULAR"): "DETAINED", ("ITITC503", "2025-DEC", "REGULAR"): (20, 12),
                       ("ITITC501", "2025-DEC", "REGULAR"): (18, 15)},
                  note="DETAINED + 2 fails = multiple backlogs (3 visible + 1 legacy = 4); CGPA exactly 5.00 (degree minimum); attendance exactly 60% (24/40, the Cl. 11.6 floor)"),
    "S1005": dict(cgpa=7.50, note="CGPA exactly 7.50 (CVSPK Talent Incentive retention threshold); all passed"),
    "S1006": dict(cgpa=7.10, res={("ITITC501", "2025-DEC", "REGULAR"): (41, 14), ("ITITC501", "2026-JUL", "SUPPLEMENTARY"): (41, 22)},
                  note="Total 55 but ESE 14/50 = 28% < 30% -> FAIL (Cl. 12.7); later cleared in SUPPLEMENTARY session"),
    "S1008": dict(cgpa=6.50, note="CGPA exactly 6.50 (First Division threshold, Cl. 15)"),
    "S1009": dict(cgpa=8.00, att={"ITITC501": (40, 30)}, note="Attendance exactly 75% (30/40) in ITITC501; CGPA exactly 8.00"),
    "S1010": dict(att={"ITITC503": (40, 29)}, note="Attendance one class below threshold (29/40 = 72.5%) in ITITC503"),
    "S1011": dict(att={"ITITC504": (40, 24)}, note="Attendance exactly 60% (24/40): at the Cl. 11.6 floor but below 75%"),
    "S1012": dict(att={"ITITC501": (41, 24)}, note="Attendance 58.5% (24/41): below the 60% floor even after relaxation"),
    "S1013": dict(cgpa=7.00, res={("ITITC302", "2025-DEC", "REGULAR"): (14, 20), ("ITITC302", "2026-JUL", "SUPPLEMENTARY"): (30, 35)},
                  note="Fail at 34, then PASS in SUPPLEMENTARY (backlog cleared)"),
    "S1014": dict(cgpa=6.60, res={("ITITC304", "2025-DEC", "REGULAR"): "ABSENT", ("ITITC304", "2026-JUL", "SUPPLEMENTARY"): "ABSENT"},
                  note="ABSENT in regular and again in SUPPLEMENTARY; backlog persists"),
    "S1016": dict(cgpa=5.60, extra_backlogs=1,
                  res={("ITITC302", "2025-DEC", "REGULAR"): (10, 10), ("ITITC304", "2025-DEC", "REGULAR"): (15, 15)},
                  note="Both semester-3 courses failed + 1 legacy backlog = 3 active backlogs"),
    "S1018": dict(cgpa=6.80, att={"COCSC501": (40, 30)}, res={("COCSC501", "2025-DEC", "REGULAR"): (14, 20)},
                  note="Fail at 34; re-registered with attendance exactly 75% (30/40)"),
    "S1019": dict(cgpa=6.20, att={"COCSC503": (40, 27)}, res={("COCSC503", "2025-DEC", "REGULAR"): "DETAINED"},
                  note="DETAINED; re-registered with 67.5% attendance (27/40)"),
    "S1020": dict(cgpa=8.50, note="CGPA exactly 8.50 (second student at the Honours cut-off)"),
    "S1021": dict(cgpa=7.50, att={"COCSC504": (36, 27)}, res={("COCSC504", "2025-DEC", "REGULAR"): (20, 10)},
                  note="CGPA 7.50; failed COCSC504 (30 total, ESE 10); re-registered at exactly 75% (27/36)"),
    "S1022": dict(cgpa=5.00, extra_backlogs=2,
                  res={("COCSC501", "2025-DEC", "REGULAR"): (18, 14), ("COCSC503", "2025-DEC", "REGULAR"): "ABSENT",
                       ("COCSC504", "2025-DEC", "REGULAR"): (22, 11)},
                  att={"COCSC501": (40, 31), "COCSC503": (40, 20), "COCSC504": (40, 33)},
                  note="3 visible + 2 legacy = 5 active backlogs; CGPA exactly 5.00; attendance 50% in COCSC503"),
    "S1025": dict(cgpa=8.00, att={"COCSC501": (40, 30)}, note="Attendance exactly 75%; CGPA exactly 8.00"),
    "S1026": dict(att={"COCSC503": (40, 29)}, note="Attendance one class below threshold (72.5%)"),
    "S1027": dict(att={"COCSC504": (40, 24)}, note="Attendance exactly 60%"),
    "S1028": dict(cgpa=6.50, res={("COCSC302", "2025-DEC", "REGULAR"): (14, 20), ("COCSC302", "2026-JUL", "SUPPLEMENTARY"): (20, 14)},
                  note="Fail at 34, then SUPPLEMENTARY also fails (total 34, ESE 14 < 15); CGPA exactly 6.50"),
    "S1029": dict(cgpa=6.80, res={("COCSC303", "2025-DEC", "REGULAR"): "ABSENT", ("COCSC303", "2026-JUL", "SUPPLEMENTARY"): (25, 30)},
                  note="ABSENT then PASS in SUPPLEMENTARY"),
    "S1032": dict(cgpa=5.40, extra_backlogs=1,
                  res={("COCSC302", "2025-DEC", "REGULAR"): (12, 9), ("COCSC303", "2025-DEC", "REGULAR"): (13, 11)},
                  note="Both semester-3 courses failed + 1 legacy backlog = 3 active backlogs"),
}


def grade(total, ext, result):
    if result == "DETAINED":
        return "FD"
    if result == "ABSENT":
        return "Ab"
    if result == "FAIL":
        return "F"
    for lo, g in [(90, "O"), (81, "A+"), (72, "A"), (63, "B+"), (54, "B"), (45, "C"), (35, "D")]:
        if total >= lo:
            return g
    return "F"


def make_result(code, session, etype, val):
    if val in ("ABSENT", "DETAINED"):
        return dict(course_code=code, exam_session=session, exam_type=etype, internal_marks=random.randint(18, 40),
                    external_marks="", total_marks="", max_marks=100, result=val, grade="Ab" if val == "ABSENT" else "FD")
    i, e = val
    t = i + e
    res = "PASS" if (t >= 35 and e >= 15) else "FAIL"
    return dict(course_code=code, exam_session=session, exam_type=etype, internal_marks=i, external_marks=e,
                total_marks=t, max_marks=100, result=res, grade=grade(t, e, res))


def passing_pair():
    while True:
        i, e = random.randint(26, 48), random.randint(22, 48)
        if 50 <= i + e <= 96:
            return i, e


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    students, attendance, results, edge_rows = [], [], [], []
    used_roll = {}
    for n, (sid, prog, batch) in enumerate(ROSTER):
        code = "UIT" if prog == IT else "UCS"
        base = 3101 if prog == IT else 2101
        k = used_roll.get((prog, batch), 0)
        used_roll[(prog, batch)] = k + 1
        roll = f"{batch}{code}{base + k}"
        name = f"{FIRST[n]} {LAST[n]}"
        e = EDGE.get(sid, {})
        cgpa = e.get("cgpa", round(random.uniform(6.2, 9.4), 2))
        sem = 7 if batch == 2023 else 5
        ccodes = SEM5[prog] if batch == 2023 else SEM3[prog]

        # Results: 2023 batch -> sem-5 courses (Dec 2025); 2024 batch -> sem-3 courses (Dec 2025).
        rows = {}
        for c in ccodes:
            rows[(c, "2025-DEC", "REGULAR")] = passing_pair()
        for key, val in e.get("res", {}).items():
            rows[key] = val
        for (c, ses, et), val in sorted(rows.items(), key=lambda kv: (kv[0][0], kv[0][1])):
            r = make_result(c, ses, et, val)
            r.update(student_id=sid)
            results.append(r)

        # Attendance: current-term rows. 2024 batch: all three sem-5 courses. 2023 batch: only Study-Mode re-registrations.
        att = {}
        if batch == 2024:
            for c in SEM5[prog]:
                held = random.randint(36, 44)
                att[c] = (held, min(held, round(held * random.uniform(0.80, 0.97))))
        for c, v in e.get("att", {}).items():
            att[c] = v
        for c, (h, a) in att.items():
            attendance.append(dict(student_id=sid, course_code=c, classes_held=h, classes_attended=a))

        # Backlogs = courses whose latest result is not PASS, plus legacy backlogs outside the 10 courses.
        latest = {}
        for r in results:
            if r["student_id"] == sid:
                key = r["course_code"]
                if key not in latest or r["exam_session"] > latest[key][0]:
                    latest[key] = (r["exam_session"], r["result"])
        backlogs = sum(1 for _, res in latest.values() if res != "PASS") + e.get("extra_backlogs", 0)
        students.append(dict(student_id=sid, full_name=name, programme=prog, batch_year=batch, current_semester=sem,
                             cgpa=f"{cgpa:.2f}", active_backlogs=backlogs, roll_no=roll,
                             email=f"{name.lower().replace(' ', '.')}.{roll.lower()}@nsut.ac.in"))
        if e.get("note"):
            edge_rows.append(dict(student_id=sid, roll_no=roll, edge_case=e["note"]))

    def dump(name, cols, rows):
        with (OUT / name).open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)

    dump("students.csv", ["student_id", "full_name", "programme", "batch_year", "current_semester", "cgpa",
                          "active_backlogs", "roll_no", "email"], students)
    dump("courses.csv", ["course_code", "course_name", "programme", "semester", "credits", "course_type"],
         [dict(zip(["course_code", "course_name", "programme", "semester", "credits", "course_type"], c)) for c in COURSES])
    dump("attendance.csv", ["student_id", "course_code", "classes_held", "classes_attended"], attendance)
    dump("results.csv", ["student_id", "course_code", "exam_session", "exam_type", "internal_marks", "external_marks",
                         "total_marks", "max_marks", "result", "grade"], results)
    dump("edge_cases.csv", ["student_id", "roll_no", "edge_case"], edge_rows)
    print(f"students={len(students)} courses={len(COURSES)} attendance={len(attendance)} results={len(results)} edge_cases={len(edge_rows)}")


if __name__ == "__main__":
    main()
