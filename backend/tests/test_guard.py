"""Privacy checks of step 1 (no LLM involved)."""
from app.pipeline.guard import guard


def test_other_student_id_is_refused():
    out = guard({"question": "Show me the attendance of S0002", "student_id": "S0001"})
    assert out["answer_type"] == "refused"


def test_friends_records_are_refused():
    out = guard({"question": "What are my friend's marks in TC201?", "student_id": "S0001"})
    assert out["answer_type"] == "refused"


def test_own_id_in_question_is_fine():
    out = guard({"question": "I am S0001, what is my attendance?", "student_id": "S0001"})
    assert out["student"]["student_id"] == "S0001"


def test_unknown_student_is_refused():
    assert guard({"question": "my attendance?", "student_id": "S0999"})["answer_type"] == "refused"


def test_policy_wording_with_their_is_not_refused():
    assert "stop" not in guard({"question": "Must students keep their attendance above the minimum?", "student_id": None})
