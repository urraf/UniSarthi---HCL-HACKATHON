"""Tests for the Source Precedence Policy, starting with the guide's own worked example (Annex A.3)."""
from app.precedence import resolve


def doc(doc_id, level, start, value, section="1", supersedes="", end="", batches="ALL"):
    return {"doc_id": doc_id, "section": section, "authority_level": level, "effective_from": start,
            "effective_to": end, "supersedes": supersedes, "scope_programmes": "ALL",
            "scope_batches": batches, "value": value, "label": doc_id}


REGULATION = doc("ACAD-REG-2024", 1, "2024-07-01", "75", section="7.2")
CIRCULAR = doc("ACAD-2026-08", 2, "2026-08-01", "80", supersedes="ACAD-REG-2024#7.2")
FAQ = doc("FAQ-2026", 4, "2026-09-15", "65")
ALL_THREE = [REGULATION, CIRCULAR, FAQ]


def test_worked_example_circular_supersedes_regulation():
    res = resolve(ALL_THREE, None, "2026-10-06")
    assert res["status"] == "resolved"
    assert res["winner"]["value"] == "80"
    reasons = {o["item"]["doc_id"]: o["reason"] for o in res["overridden"]}
    assert "supersession" in reasons["ACAD-REG-2024"]
    assert "authority" in reasons["FAQ-2026"]


def test_before_circular_regulation_applies_and_circular_is_upcoming():
    res = resolve(ALL_THREE, None, "2026-07-15")
    assert res["winner"]["value"] == "75"
    assert [u["doc_id"] for u in res["upcoming"]] == ["ACAD-2026-08", "FAQ-2026"]


def test_higher_authority_wins_even_if_older():
    old_reg = doc("REG", 1, "2020-01-01", "75")
    new_notice = doc("NOTICE", 3, "2026-01-01", "70")
    assert resolve([old_reg, new_notice], None, "2026-10-06")["winner"]["doc_id"] == "REG"


def test_same_authority_newer_wins():
    a = doc("CIRC-A", 2, "2025-01-01", "70")
    b = doc("CIRC-B", 2, "2026-01-01", "72")
    assert resolve([a, b], None, "2026-10-06")["winner"]["doc_id"] == "CIRC-B"


def test_unresolved_conflict_is_flagged():
    a = doc("CIRC-A", 2, "2026-01-01", "70")
    b = doc("CIRC-B", 2, "2026-01-01", "72")
    res = resolve([a, b], None, "2026-10-06")
    assert res["status"] == "conflict"
    assert {t["doc_id"] for t in res["tied"]} == {"CIRC-A", "CIRC-B"}


def test_unofficial_never_wins():
    reg = doc("REG", 1, "2024-01-01", "75")
    rumour = doc("FORUM", 5, "2026-09-01", "0")
    res = resolve([reg, rumour], None, "2026-10-06")
    assert res["winner"]["doc_id"] == "REG"


def test_only_level_1_or_2_can_supersede():
    reg = doc("REG", 1, "2024-01-01", "75", section="7.2")
    dept = doc("DEPT", 3, "2026-01-01", "60", supersedes="REG#7.2")
    assert resolve([reg, dept], None, "2026-10-06")["winner"]["doc_id"] == "REG"


def test_batch_scope():
    general = doc("POL", 2, "2025-07-01", "6.5", section="3.1")
    revised = doc("CIRC", 2, "2026-12-01", "7.0", supersedes="POL#3.1", batches="2024+")
    old_student = {"programme": "B.Tech CSE", "batch_year": 2023}
    new_student = {"programme": "B.Tech CSE", "batch_year": 2024}
    assert resolve([general, revised], old_student, "2027-01-01")["winner"]["value"] == "6.5"
    assert resolve([general, revised], new_student, "2027-01-01")["winner"]["value"] == "7.0"
