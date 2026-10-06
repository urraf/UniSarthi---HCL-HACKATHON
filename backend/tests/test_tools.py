"""Tests for the deterministic tools against NSUT's real rule registry (see data/rules_seed.csv)."""
from app import tools

TODAY = "2026-10-06"
PLACEMENT_SEASON = "2025-03-01"  # inside the 2024-25 placement policy (it expired on 2025-06-30)


def test_attendance_is_computed_not_stored():
    assert tools.get_attendance("S0002", "TC201")["attendance_pct"] == 72.5


def test_exactly_75_percent_is_eligible():
    res = tools.check_exam_eligibility("S0001", "TC201", TODAY)
    assert res["result"] == "ELIGIBLE"
    assert res["rule"]["value"] == "75"


def test_one_class_below_75_is_not_eligible_but_relaxation_is_mentioned():
    res = tools.check_exam_eligibility("S0002", "TC201", TODAY)
    assert res["result"] == "NOT_ELIGIBLE"
    assert "relax" in res["note"]


def test_below_the_60_percent_floor_no_relaxation():
    res = tools.check_exam_eligibility("S0003", "TC201", TODAY)
    assert res["result"] == "NOT_ELIGIBLE"
    assert "floor" in res["below_floor"]


def test_no_supplementary_exam_at_nsut():
    assert tools.check_supplementary_eligibility("S0002", "TC202", TODAY)["result"] == "NOT_AVAILABLE"


def test_passed_course_needs_nothing():
    assert tools.check_supplementary_eligibility("S0001", "TC201", TODAY)["result"] == "NOT_NEEDED"


def test_placement_no_cgpa_minimum_and_no_backlogs():
    res = tools.check_placement_eligibility("S0001", PLACEMENT_SEASON)
    assert res["result"] == "ELIGIBLE"
    assert "no university-wide minimum" in res["cgpa_required"]


def test_placement_too_many_backlogs():
    assert tools.check_placement_eligibility("S0002", PLACEMENT_SEASON)["result"] == "NOT_ELIGIBLE"  # 3 > 2


def test_what_if_clearing_one_backlog_makes_placement_possible():
    what_if = tools.check_placement_eligibility("S0002", PLACEMENT_SEASON, assume_cleared=["TC202"])
    assert what_if["active_backlogs_used"] == 2
    assert what_if["result"] == "ELIGIBLE"
    assert what_if["assumptions"]


def test_placement_policy_expired_today():
    res = tools.check_placement_eligibility("S0001", TODAY)
    assert res["result"] == "UNDETERMINED"
    assert "expired" in res["reason"]
