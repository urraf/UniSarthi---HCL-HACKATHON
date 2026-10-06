"""
The shared "state" that flows through the LangGraph pipeline.

Each step reads what it needs and returns only the keys it changes.
If a step sets stop=True, the graph jumps straight to the finalize step.
"""
from typing import TypedDict

# What the assistant can do. The LLM must pick one of these for every question.
# Rule of thumb: "what IS the rule?" -> policy;  "what is MY situation?" -> a personal intent.
INTENTS = {
    "policy": "general question about university rules, procedures (e.g. how to apply), fees or documents; not about the student's own records",
    "my_courses": "the student's own subjects / courses: their names, how many, which ones",
    "my_attendance": "the student's own attendance (in one course, or in all courses if none is named)",
    "my_profile": "the student's own CGPA, number of backlogs, current semester, programme or batch",
    "my_results": "the student's own marks or results in courses",
    "exam_eligibility": "can the student appear in the end-semester exam of a course",
    "supplementary_eligibility": "can the student take the supplementary exam in a course",
    "placement_eligibility": "can the student register for campus placements",
    "placement_whatif": "placement eligibility IF the student passes a failed course (what-if)",
    "small_talk": "ONLY greetings, thanks, 'who are you' or 'what can you do'. Any real question, even off-topic, is policy",
}
# Intents that need the logged-in student's own records
PERSONAL_INTENTS = {"my_profile", "my_courses", "my_attendance", "my_results", "exam_eligibility", "supplementary_eligibility",
                    "placement_eligibility", "placement_whatif"}
# Intents that need to know which course
COURSE_INTENTS = {"my_attendance", "exam_eligibility", "supplementary_eligibility", "placement_whatif"}


class State(TypedDict, total=False):
    # ---- input ----
    question: str
    as_of: str                  # YYYY-MM-DD
    student_id: str | None      # from the X-Student-Id header / login token, never from the text
    started_at: float

    # ---- step 1: guard ----
    student: dict | None        # the student's profile row

    # ---- step 2: understand ----
    intent: str
    course_code: str | None
    search_query: str           # the question rewritten for document search (better recall)
    overview: bool              # broad question ("university rules"): answer with an overview of the key rules
    rule_parameters: list[str]  # rule registry parameters the question is about

    # ---- step 3: find ----
    evidence: list[dict]        # document chunks, best first
    upcoming: list[dict]        # documents not yet in force
    rules: list[dict]           # resolved rules (from get_rule / tools)

    # ---- step 4: calculate ----
    tools_invoked: list[dict]
    assumptions: list[str]

    # ---- step 5: answer ----
    answer: str
    explanation: str
    answer_type: str
    used_evidence: list[str]    # evidence ids the answer is based on
    conflicts: list[dict]

    # ---- finalize ----
    response: dict              # the JSON returned by POST /ask

    # ---- bookkeeping ----
    stop: bool                  # True -> skip to finalize
    llm_calls: int
    tokens: int
    models_used: list[str]      # models that actually answered (Groq fallbacks / local Ollama)
    llm_fallback: bool          # True if a step used keyword/template fallback instead of the LLM
