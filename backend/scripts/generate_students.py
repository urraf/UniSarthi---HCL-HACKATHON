"""
Generate synthetic student data with an LLM, in the guide's fixed schema (Annex C).

How it works:
  1. Read the plan (data/prompts/generation_plan.json): programmes, batches, courses, edge cases.
  2. For each group of 8 students, fill the prompt template and ask the LLM for JSON.
  3. Check the JSON with Pydantic. If it is invalid, tell the LLM what was wrong and retry.
  4. Code (not the LLM) computes the derived fields: total_marks and active_backlogs.
  5. Write CSV files to data/students/ and a log of every fix to generation_log.json.

Run:  python scripts/generate_students.py
"""
import csv
import json
import sys
from pathlib import Path
from string import Template
from typing import Literal

from pydantic import BaseModel, Field, ValidationError, model_validator

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app import config  # noqa: E402
from app.llm import LLMError, chat_json  # noqa: E402

PROMPTS = config.DATA_DIR / "prompts"
OUT_DIR = config.DATA_DIR / "students"
SYSTEM = "You generate realistic synthetic test data. You always reply with valid JSON only."
TEMPERATURE = 0.7
MAX_ATTEMPTS = 3


# ---------- What we expect back from the LLM (schema enforcement) ----------
class GenCourse(BaseModel):
    course_code: str
    classes_held: int = Field(ge=1)
    classes_attended: int = Field(ge=0)
    internal_marks: int = Field(ge=0)
    external_marks: int = Field(ge=0)
    result: Literal["PASS", "FAIL", "ABSENT", "DETAINED"]

    @model_validator(mode="after")
    def attended_not_more_than_held(self):
        if self.classes_attended > self.classes_held:
            raise ValueError(f"{self.course_code}: classes_attended > classes_held")
        return self


class GenStudent(BaseModel):
    student_id: str = Field(pattern=r"^S\d{4}$")
    full_name: str = Field(min_length=3)
    cgpa: float = Field(ge=0, le=10)
    courses: list[GenCourse]


class GenOutput(BaseModel):
    students: list[GenStudent]


def pass_mark_from_rules(max_marks: int) -> int:
    """Pass mark comes from the rule registry seed file, not from code."""
    with open(config.DATA_DIR / "rules_seed.csv") as f:
        for rule in csv.DictReader(f):
            if rule["parameter"] == "pass_marks_pct":
                return round(float(rule["value"]) * max_marks / 100)
    raise SystemExit("pass_marks_pct rule not found in rules_seed.csv")


def build_prompt(template: Template, plan: dict, group: dict, pass_mark: int) -> tuple[str, list[str], list[str]]:
    """Fill the prompt template for one group of students."""
    ids = [f"S{group['first_id'] + i}" for i in range(group["count"])]
    courses = [c for c in plan["courses"]
               if c["programme"] == group["programme"] and c["semester"] == group["course_semester"]]
    prompt = template.substitute(
        programme=group["programme"],
        batch_year=group["batch_year"],
        current_semester=group["current_semester"],
        count=group["count"],
        id_list=", ".join(ids),
        exam_session=plan["exam_session"],
        course_semester=group["course_semester"],
        course_list="\n".join(f"  - {c['course_code']} {c['course_name']}" for c in courses),
        internal_max=plan["internal_max"],
        external_max=plan["external_max"],
        pass_mark=pass_mark,
        edge_cases="\n".join(f"- {e}" for e in group["edge_cases"]),
    )
    return prompt, ids, [c["course_code"] for c in courses]


def check_group(out: GenOutput, ids: list[str], course_codes: list[str], plan: dict) -> None:
    """Extra checks Pydantic cannot do alone: right IDs, right courses, marks in range."""
    got_ids = [s.student_id for s in out.students]
    if got_ids != ids:
        raise ValueError(f"expected student IDs {ids}, got {got_ids}")
    for s in out.students:
        if sorted(c.course_code for c in s.courses) != sorted(course_codes):
            raise ValueError(f"{s.student_id}: expected courses {course_codes}")
        for c in s.courses:
            if c.internal_marks > plan["internal_max"] or c.external_marks > plan["external_max"]:
                raise ValueError(f"{s.student_id} {c.course_code}: marks above maximum")


def generate_group(template, plan, group, pass_mark, log) -> GenOutput:
    """Ask the LLM for one group; retry with the error message if the output is invalid."""
    prompt, ids, course_codes = build_prompt(template, plan, group, pass_mark)
    for attempt in range(1, MAX_ATTEMPTS + 1):
        data, usage = chat_json(SYSTEM, prompt, temperature=TEMPERATURE)
        log["llm_calls"] += usage["calls"]
        log["tokens"] += usage["tokens"]
        try:
            out = GenOutput.model_validate(data)
            check_group(out, ids, course_codes, plan)
            return out
        except (ValidationError, ValueError) as e:
            log["retries"].append({"group": f"{group['programme']} {group['batch_year']}",
                                   "attempt": attempt, "error": str(e)[:300]})
            prompt += f"\n\nYour previous answer was invalid: {str(e)[:300]}\nReturn corrected JSON only."
    raise SystemExit(f"Group {group['programme']} {group['batch_year']} failed after {MAX_ATTEMPTS} attempts")


def main() -> None:
    plan = json.loads((PROMPTS / "generation_plan.json").read_text())
    template = Template((PROMPTS / "students_prompt.txt").read_text())
    pass_mark = pass_mark_from_rules(plan["max_marks"])
    log = {"model": config.active_model_name(), "temperature": TEMPERATURE,
           "llm_calls": 0, "tokens": 0, "retries": [], "fixes": []}

    students, attendance, results = [], [], []
    for group in plan["groups"]:
        print(f"Generating {group['count']} students: {group['programme']} batch {group['batch_year']} ...")
        out = generate_group(template, plan, group, pass_mark, log)

        for s in out.students:
            backlogs = 0
            for c in s.courses:
                attendance.append([s.student_id, c.course_code, c.classes_held, c.classes_attended])
                # Derived field: computed by code, never trusted from the LLM
                total = c.internal_marks + c.external_marks
                result = c.result
                # Fix results that contradict the marks (logged for the data card)
                if result in ("PASS", "FAIL"):
                    correct = "PASS" if total >= pass_mark else "FAIL"
                    if correct != result:
                        log["fixes"].append(f"{s.student_id} {c.course_code}: LLM said {result} for total {total}, fixed to {correct}")
                        result = correct
                elif c.external_marks != 0:
                    log["fixes"].append(f"{s.student_id} {c.course_code}: {result} with external_marks {c.external_marks}, set to 0")
                    total = c.internal_marks
                    c.external_marks = 0
                if result != "PASS":
                    backlogs += 1
                results.append([s.student_id, c.course_code, plan["exam_session"], "REGULAR",
                                c.internal_marks, c.external_marks, total, plan["max_marks"], result])
            students.append([s.student_id, s.full_name, group["programme"], group["batch_year"],
                             group["current_semester"], round(s.cgpa, 2), backlogs])

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_csv("students.csv", ["student_id", "full_name", "programme", "batch_year", "current_semester",
                               "cgpa", "active_backlogs"], students)
    write_csv("courses.csv", ["course_code", "course_name", "programme", "semester", "credits"],
              [[c["course_code"], c["course_name"], c["programme"], c["semester"], c["credits"]] for c in plan["courses"]])
    write_csv("attendance.csv", ["student_id", "course_code", "classes_held", "classes_attended"], attendance)
    write_csv("results.csv", ["student_id", "course_code", "exam_session", "exam_type", "internal_marks",
                              "external_marks", "total_marks", "max_marks", "result"], results)
    (OUT_DIR / "generation_log.json").write_text(json.dumps(log, indent=2))
    print(f"Done: {len(students)} students. LLM calls={log['llm_calls']}, fixes={len(log['fixes'])}")
    print("Next: python scripts/validate_data.py")


def write_csv(name: str, header: list[str], rows: list[list]) -> None:
    with open(OUT_DIR / name, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


if __name__ == "__main__":
    try:
        main()
    except LLMError as e:
        raise SystemExit(f"LLM not available: {e}\nSet LLM_PROVIDER and keys in backend/.env")
