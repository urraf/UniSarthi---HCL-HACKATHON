"""
Step 1 - Check who is asking (no LLM).

- The student's identity comes ONLY from the request (X-Student-Id header / login token),
  never from the question text (R7).
- A question that names another student ID, or asks about someone else's data, is refused.
"""
import re

from app import tools
from app.pipeline.state import State

STUDENT_ID = re.compile(r"\bS\d{4}\b", re.IGNORECASE)
# Phrases that mean "someone else's records"
OTHER_PERSON = re.compile(
    r"\b(my friend'?s?|another student'?s?|other student'?s?|classmate'?s?|roommate'?s?)\s+"
    r"(attendance|marks|results?|cgpa|grades?|backlogs?|records?|eligibility)\b",
    re.IGNORECASE,
)


def guard(state: State) -> dict:
    question = state["question"]
    own_id = (state.get("student_id") or "").upper()

    # Another student's ID in the question
    for found in STUDENT_ID.findall(question):
        if found.upper() != own_id:
            return refuse("I can only share your own records. Requests for another student's data are not allowed.")

    if OTHER_PERSON.search(question):
        return refuse("I can only share your own records. Requests for another student's data are not allowed.")

    # Unknown student ID in the header
    student = None
    if own_id:
        student = tools.get_student_profile(own_id)
        if student is None:
            return refuse(f"Student ID {own_id} is not registered.")

    return {"student": student}


def refuse(message: str) -> dict:
    return {"stop": True, "answer_type": "refused", "answer": message,
            "explanation": "Refused by the privacy check (step 1)."}
