"""
The LangGraph pipeline: 5 steps + finalize, in a fixed order.

    guard -> understand -> find -> [calculate] -> write_answer -> finalize

- calculate only runs for personal questions (they need the student's records).
- Any step can set stop=True (refused, clarification_needed, not_found): the graph
  then jumps straight to finalize, so every request still gets a trace_id and audit row.

Why one simple graph and not several agents? Every question goes through the same steps
in the same order, and the decisions are deterministic code. More agents would add
latency and failure points without making answers more accurate.
"""
import time
from datetime import date

from langgraph.graph import END, StateGraph

from app.pipeline.answer import answer
from app.pipeline.calculate import calculate
from app.pipeline.find import find
from app.pipeline.finalize import finalize
from app.pipeline.guard import guard
from app.pipeline.state import PERSONAL_INTENTS, State
from app.pipeline.understand import understand


def stop_or(next_step: str):
    """Edge helper: go to finalize if a step stopped the request, else to next_step."""
    return lambda state: "finalize" if state.get("stop") else next_step


def after_find(state: State) -> str:
    if state.get("stop"):
        return "finalize"
    return "calculate" if state["intent"] in PERSONAL_INTENTS else "write_answer"


def build_graph():
    g = StateGraph(State)
    g.add_node("guard", guard)
    g.add_node("understand", understand)
    g.add_node("find", find)
    g.add_node("calculate", calculate)
    g.add_node("write_answer", answer)  # node names must differ from state keys
    g.add_node("finalize", finalize)

    g.set_entry_point("guard")
    g.add_conditional_edges("guard", stop_or("understand"), ["understand", "finalize"])
    g.add_conditional_edges("understand", stop_or("find"), ["find", "finalize"])
    g.add_conditional_edges("find", after_find, ["calculate", "write_answer", "finalize"])
    g.add_edge("calculate", "write_answer")
    g.add_edge("write_answer", "finalize")
    g.add_edge("finalize", END)
    return g.compile()


# Built once when the app starts
PIPELINE = build_graph()


def run(question: str, student_id: str | None, as_of: str | None = None) -> dict:
    """Run one question through the pipeline and return the API response dict."""
    state = {"question": question, "student_id": student_id,
             "as_of": as_of or date.today().isoformat(), "started_at": time.time(),
             "llm_calls": 0, "tokens": 0}
    return PIPELINE.invoke(state)["response"]
