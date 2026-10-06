"""
Deterministic tools: plain Python over SQLite.

Rules of this file:
  - No LLM here. Every number and every ELIGIBLE / NOT_ELIGIBLE comes from code.
  - No thresholds typed in the code. They are read from rule_registry via get_rule(),
    which applies the precedence policy for the student's programme, batch and date.
  - student_id is always passed in by the pipeline (from the login/header),
    never chosen by the LLM.
"""
from app import db
from app.precedence import resolve


# ---------- Student data ----------
def get_student_profile(student_id: str) -> dict | None:
    return db.query_one("SELECT * FROM students WHERE student_id = ?", (student_id,))


def get_attendance(student_id: str, course_code: str) -> dict:
    row = db.query_one(
        "SELECT a.course_code, c.course_name, a.classes_held, a.classes_attended "
        "FROM attendance a JOIN courses c ON c.course_code = a.course_code "
        "WHERE a.student_id = ? AND a.course_code = ?",
        (student_id, course_code),
    )
    if not row:
        return {"error": f"You have no attendance record for {course_code} (attendance is only recorded "
                         "for courses you are currently registered in)"}
    # Attendance % is computed here, never stored (guide, Annex C)
    row["attendance_pct"] = round(100 * row["classes_attended"] / row["classes_held"], 2)
    return row


def get_results(student_id: str, course_code: str | None = None) -> list[dict]:
    sql = ("SELECT r.course_code, c.course_name, r.exam_session, r.exam_type, r.internal_marks, "
           "r.external_marks, r.total_marks, r.max_marks, r.result "
           "FROM results r JOIN courses c ON c.course_code = r.course_code WHERE r.student_id = ?")
    params = [student_id]
    if course_code:
        sql += " AND r.course_code = ?"
        params.append(course_code)
    return db.query(sql + " ORDER BY r.exam_session DESC", tuple(params))


# ---------- Rules ----------
def get_rule(parameter: str, student: dict | None, as_of: str) -> dict:
    """
    Find the rule that applies for this parameter, student and date.
    Rules come from rule_registry; authority and supersession come from the document they cite.
    """
    rows = db.query(
        "SELECT r.*, d.authority_level, d.supersedes, d.title "
        "FROM rule_registry r JOIN documents d ON d.doc_id = r.source_doc_id "
        "WHERE r.parameter = ?",
        (parameter,),
    )
    items = [{**r, "doc_id": r["source_doc_id"], "section": r["source_section"], "label": r["rule_id"]} for r in rows]
    res = resolve(items, student, as_of)
    w = res["winner"]
    if res["status"] == "none":
        # Say WHY there is no rule: e.g. the only policy expired before as_of_date
        expired = sorted((i for i in items if i.get("effective_to") and i["effective_to"] < as_of),
                         key=lambda i: i["effective_to"])
        if expired:
            last = expired[-1]
            res["decision"] = (f"No rule in force on {as_of}: the latest one ({last['rule_id']}, {last['doc_id']}) "
                               f"expired on {last['effective_to']}.")
    return {
        "parameter": parameter,
        "status": res["status"],                          # resolved | conflict | none
        "rule_id": w["rule_id"] if w else None,
        "operator": w["operator"] if w else None,
        "value": w["value"] if w else None,
        "source_doc_id": w["source_doc_id"] if w else None,
        "source_section": w["source_section"] if w else None,
        "decision": res["decision"],
        "overridden": [{"rule_id": o["item"]["rule_id"], "doc_id": o["item"]["doc_id"],
                        "value": o["item"]["value"], "reason": o["reason"]} for o in res["overridden"]],
        "tied": [{"rule_id": t["rule_id"], "doc_id": t["doc_id"], "value": t["value"]} for t in res["tied"]],
        "upcoming": [{"rule_id": u["rule_id"], "doc_id": u["doc_id"], "value": u["value"],
                      "effective_from": u["effective_from"]} for u in res["upcoming"]],
    }


def compare(actual, operator: str, threshold: str) -> bool:
    """Apply a rule's operator. Values are stored as text in the registry."""
    if operator == "in":
        return str(actual) in [v.strip() for v in threshold.replace(",", ";").split(";")]
    a, t = float(actual), float(threshold)
    return {">=": a >= t, "<=": a <= t, ">": a > t, "<": a < t, "==": a == t}[operator]


def _undetermined(rule: dict) -> dict:
    """Used when the rule itself cannot be decided (conflict or missing)."""
    return {"result": "UNDETERMINED", "reason": rule["decision"], "rule": rule}


def first_rule(parameters: list[str], student: dict | None, as_of: str) -> dict:
    """The first of these registry parameters that has a rule (registries name things differently)."""
    rule = None
    for parameter in parameters:
        rule = get_rule(parameter, student, as_of)
        if rule["status"] != "none":
            return rule
    return rule


# ---------- Eligibility checks ----------
def check_exam_eligibility(student_id: str, course_code: str, as_of: str) -> dict:
    """Can the student sit the end-semester exam in this course? (attendance rules)"""
    student = get_student_profile(student_id)
    attendance = get_attendance(student_id, course_code)
    if "error" in attendance:
        return attendance
    rule = get_rule("min_attendance_pct", student, as_of)
    if rule["status"] != "resolved":
        return _undetermined(rule)
    pct = attendance["attendance_pct"]
    out = {"attendance_pct": pct, "required": f"{rule['operator']} {rule['value']}%", "rule": rule}
    if compare(pct, rule["operator"], rule["value"]):
        return {"result": "ELIGIBLE", **out}

    # Short of attendance: is a relaxation by the Dean possible, or is the student below the hard floor?
    floor = get_rule("attendance_floor_pct", student, as_of)
    relax = get_rule("attendance_relaxation_pct", student, as_of)
    rules = [rule] + [r for r in (floor, relax) if r["status"] == "resolved"]
    if floor["status"] == "resolved" and not compare(pct, floor["operator"], floor["value"]):
        return {"result": "NOT_ELIGIBLE", **out, "below_floor": f"below the {floor['value']}% floor: no relaxation possible",
                "rules": rules}
    note = (f"short of attendance; the Dean may relax it by up to {relax['value']} percentage points on documented grounds"
            if relax["status"] == "resolved" else "short of attendance")
    return {"result": "NOT_ELIGIBLE", **out, "note": note, "rules": rules}


def check_supplementary_eligibility(student_id: str, course_code: str, as_of: str) -> dict:
    """Can the student take a supplementary exam in this course?"""
    student = get_student_profile(student_id)
    results = get_results(student_id, course_code)
    if not results:
        return {"error": f"You have no exam result for {course_code}"}
    latest = results[0]
    if latest["result"] == "PASS":
        return {"result": "NOT_NEEDED", "latest_result": "PASS", "course_code": course_code}

    # Registry says supplementary exams do not exist at all (e.g. NSUT Regulations Cl. 12.3)
    allowed = get_rule("supplementary_allowed", student, as_of)
    if allowed["status"] == "resolved" and str(allowed["value"]).lower() in ("false", "no", "0"):
        return {"result": "NOT_AVAILABLE", "course_code": course_code, "latest_result": latest["result"],
                "reason": "there are no supplementary examinations; the course must be re-registered "
                          "(see the backlog / make-up exam documents)", "rule": allowed}

    # Registry lists which results may take the supplementary exam
    rule = get_rule("supplementary_allowed_results", student, as_of)
    if rule["status"] != "resolved":
        return _undetermined(rule)
    eligible = compare(latest["result"], rule["operator"], rule["value"])
    return {"result": "ELIGIBLE" if eligible else "NOT_ELIGIBLE", "course_code": course_code,
            "latest_result": latest["result"], "allowed_results": rule["value"], "rule": rule}


def check_placement_eligibility(student_id: str, as_of: str, assume_cleared: list[str] | None = None) -> dict:
    """
    Can the student register for placements? (CGPA rule + backlog rule)
    assume_cleared: what-if courses the student expects to clear.
    """
    student = get_student_profile(student_id)
    cgpa_rule = first_rule(["placement_min_cgpa", "univ_min_cgpa_placement"], student, as_of)
    backlog_rule = first_rule(["placement_max_backlogs", "max_dropped_backlogs"], student, as_of)
    for rule in (cgpa_rule, backlog_rule):
        if rule["status"] != "resolved":
            return _undetermined(rule)

    backlogs = student["active_backlogs"]
    assumptions = []
    for code in assume_cleared or []:
        latest = get_results(student_id, code)
        if latest and latest[0]["result"] != "PASS":
            backlogs -= 1
            assumptions.append(f"Assumes you clear {code}, reducing active backlogs by 1")
    if assumptions:
        assumptions.append("Assumes your CGPA stays the same (the new grade is not known yet)")

    # "none" means the university sets no minimum CGPA (companies set their own)
    no_minimum = str(cgpa_rule["value"]).lower() in ("none", "")
    cgpa_ok = True if no_minimum else compare(student["cgpa"], cgpa_rule["operator"], cgpa_rule["value"])
    backlog_ok = compare(backlogs, backlog_rule["operator"], backlog_rule["value"])
    return {
        "result": "ELIGIBLE" if cgpa_ok and backlog_ok else "NOT_ELIGIBLE",
        "cgpa": student["cgpa"],
        "cgpa_required": "no university-wide minimum (each company sets its own)" if no_minimum
        else f"{cgpa_rule['operator']} {cgpa_rule['value']}",
        "cgpa_ok": cgpa_ok,
        "active_backlogs_now": student["active_backlogs"],
        "active_backlogs_used": backlogs,
        "backlogs_allowed": f"{backlog_rule['operator']} {backlog_rule['value']}",
        "backlogs_ok": backlog_ok,
        "assumptions": assumptions,
        "rules": [cgpa_rule, backlog_rule],
    }
