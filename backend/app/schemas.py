"""
Request and response formats (Pydantic v2). These ARE the API contract of section 6 of the guide.
FastAPI checks every request against them and shows them in the docs at /docs.
"""
from typing import Literal

from pydantic import BaseModel, Field

AnswerType = Literal["retrieved_fact", "calculated", "not_found", "clarification_needed", "refused", "conflict_flagged"]


class AskRequest(BaseModel):
    question: str = Field(min_length=2, max_length=1000)
    as_of_date: str | None = Field(default=None, pattern=r"^\d{4}-\d{2}-\d{2}$", description="YYYY-MM-DD, defaults to today")


class Citation(BaseModel):
    doc_id: str
    title: str
    section: str
    page: int | None
    version: str
    effective_from: str


class ToolCall(BaseModel):
    tool: str
    input: dict
    output: dict | list | None


class AppliedRule(BaseModel):
    rule_id: str
    parameter: str
    value: str
    source_doc_id: str
    source_section: str


class AskResponse(BaseModel):
    trace_id: str
    answer: str
    answer_type: AnswerType
    citations: list[Citation]
    tools_invoked: list[ToolCall]
    applied_rules: list[AppliedRule]
    conflicts_detected: list[dict]
    explanation: str
    as_of_date: str


class IngestResponse(BaseModel):
    doc_id: str
    chunks_indexed: int
    status: str
    rules_added: list[dict]


class LoginRequest(BaseModel):
    student_id: str = Field(pattern=r"^S\d{4}$")
    password: str = Field(min_length=1)


class LoginResponse(BaseModel):
    token: str
    student_id: str
    full_name: str
    programme: str
    batch_year: int
