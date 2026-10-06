"""Tests for the deterministic tools, using the edge-case students from conftest.py."""
from app import tools

TODAY = "2026-10-06"          # circular ACAD-2026-08 (80%) is in force
BEFORE_CIRCULAR = "2026-07-15"  # regulation clause 7.2 (75%) is in force


def test_attendance_is_computed_not_stored():
    att = tools.get_attendance("S0002", "TC201")
    assert att["attendance_pct"] == 78.0


def test_exactly_at_threshold_is_eligible():
    res = tools.check_exam_eligibility("S0001", "TC201", TODAY)
    assert res["result"] == "ELIGIBLE"
    assert res["rule"]["rule_id"] == "ATT-MIN-02"


def test_one_class_below_threshold_is_not_eligible():
    assert tools.check_exam_eligibility("S0002", "TC201", TODAY)["result"] == "NOT_ELIGIBLE"


def test_same_student_was_eligible_before_the_circular():
    res = tools.check_exam_eligibility("S0002", "TC201", BEFORE_CIRCULAR)
    assert res["result"] == "ELIGIBLE"
    assert res["rule"]["rule_id"] == "ATT-MIN-01"


def test_failed_student_can_take_supplementary():
    assert tools.check_supplementary_eligibility("S0002", "TC202", TODAY)["result"] == "ELIGIBLE"


def test_detained_student_cannot_take_supplementary():
    assert tools.check_supplementary_eligibility("S0003", "TC201", TODAY)["result"] == "NOT_ELIGIBLE"


def test_passed_course_needs_no_supplementary():
    assert tools.check_supplementary_eligibility("S0001", "TC201", TODAY)["result"] == "NOT_NEEDED"


def test_cgpa_exactly_at_cutoff_is_eligible_for_placement():
    assert tools.check_placement_eligibility("S0001", TODAY)["result"] == "ELIGIBLE"


def test_upcoming_cgpa_rule_applies_after_its_date():
    # PLACE-2026-11 raises the cut-off to 7.0 for batch 2024+ from 2026-12-01
    assert tools.check_placement_eligibility("S0001", "2026-12-15")["result"] == "NOT_ELIGIBLE"


def test_what_if_passing_the_supplementary_clears_the_backlog():
    assert tools.check_placement_eligibility("S0002", TODAY)["result"] == "NOT_ELIGIBLE"
    what_if = tools.check_placement_eligibility("S0002", TODAY, assume_cleared=["TC202"])
    assert what_if["result"] == "ELIGIBLE"
    assert what_if["assumptions"]


def test_what_if_cannot_clear_a_detained_course():
    # S0003 is DETAINED in TC201: no supplementary allowed, so the backlog stays
    what_if = tools.check_placement_eligibility("S0003", TODAY, assume_cleared=["TC201"])
    assert what_if["active_backlogs_used"] == 1
    assert what_if["result"] == "NOT_ELIGIBLE"
