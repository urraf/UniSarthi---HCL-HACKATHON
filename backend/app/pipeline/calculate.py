"""
Step 4 - Calculate with code (no LLM).

The LLM chose the intent in step 2; here CODE chooses which tools run, in a fixed order.
Small local/cloud models are unreliable at choosing tools themselves, and a fixed plan
is easy to test and explain. Adding a new question type = adding one entry to PLANS.

The student_id always comes from the state (login/header), never from the LLM.
"""
import time

from app import tools
from app.pipeline.state import State

# intent -> list of (tool name, which arguments it needs)
PLANS = {
    "my_courses": [("get_courses", [])],
    "my_attendance": [("get_attendance", ["course_code"])],
    "my_results": [("get_results", ["course_code"])],
    "exam_eligibility": [("get_attendance", ["course_code"]),
                         ("check_exam_eligibility", ["course_code", "as_of"])],
    "supplementary_eligibility": [("get_results", ["course_code"]),
                                  ("check_supplementary_eligibility", ["course_code", "as_of"])],
    "placement_eligibility": [("get_student_profile", []),
                              ("check_placement_eligibility", ["as_of"])],
    "placement_whatif": [("get_results", ["course_code"]),
                         ("check_supplementary_eligibility", ["course_code", "as_of"]),
                         ("check_placement_eligibility", ["as_of", "assume_cleared"])],
}

TOOLS = {
    "get_student_profile": tools.get_student_profile,
    "get_courses": tools.get_courses,
    "get_attendance": tools.get_attendance,
    "get_results": tools.get_results,
    "check_exam_eligibility": tools.check_exam_eligibility,
    "check_supplementary_eligibility": tools.check_supplementary_eligibility,
    "check_placement_eligibility": tools.check_placement_eligibility,
}


def calculate(state: State) -> dict:
    student_id = state["student"]["student_id"]
    available = {
        "course_code": state.get("course_code"),
        "as_of": state["as_of"],
        "assume_cleared": [state["course_code"]] if state.get("course_code") else [],
    }

    invoked, rules, assumptions = [], list(state.get("rules", [])), []
    for tool_name, arg_names in PLANS.get(state["intent"], []):
        args = {name: available[name] for name in arg_names}
        start = time.time()
        output = TOOLS[tool_name](student_id, **args)
        ms = int((time.time() - start) * 1000)

        # Rules used by a tool are reported separately (applied_rules), not inside the tool output
        if isinstance(output, dict):
            rules += [output[k] for k in ("rule",) if k in output] + output.get("rules", [])
            assumptions += output.get("assumptions", [])
            output = {k: v for k, v in output.items() if k not in ("rule", "rules")}
        invoked.append({"tool": tool_name, "input": args, "output": output, "status": "ok", "ms": ms})

    unique_rules = list({r["parameter"]: r for r in rules}.values())  # one entry per rule parameter
    return {"tools_invoked": invoked, "rules": unique_rules, "assumptions": assumptions}
