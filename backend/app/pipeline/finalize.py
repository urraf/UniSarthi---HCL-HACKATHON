"""
Finalize - build the API response and save the audit record (no LLM).

- answer_type is decided by CODE, not by the LLM (R9):
    refused / clarification_needed / not_found  -> already set by an earlier step
    unresolved conflict                          -> conflict_flagged
    tools were used                              -> calculated
    otherwise                                    -> retrieved_fact
- Citations are built from document metadata (R2), never from LLM text.
- Every response gets a trace_id and an audit row (R10).
"""
import json
import time
import uuid
from datetime import datetime, timezone

from app import config, db
from app.pipeline.find import citation_for
from app.pipeline.state import State


def finalize(state: State) -> dict:
    answer_type = state.get("answer_type") or decide_answer_type(state)
    citations = build_citations(state) if answer_type in ("retrieved_fact", "calculated", "conflict_flagged") else []
    applied_rules = [{"rule_id": r["rule_id"], "parameter": r["parameter"], "value": f"{r['operator']}{r['value']}",
                      "source_doc_id": r["source_doc_id"], "source_section": r["source_section"]}
                     for r in state.get("rules", []) if r["status"] == "resolved"]
    if answer_type == "conflict_flagged" and "contact" not in state.get("answer", "").lower():
        state["answer"] = state.get("answer", "") + " The sources conflict: please contact the issuing office."

    response = {
        "trace_id": uuid.uuid4().hex[:8],
        "answer": state.get("answer", ""),
        "answer_type": answer_type,
        "citations": citations,
        "tools_invoked": [{"tool": t["tool"], "input": t["input"], "output": t["output"]}
                          for t in state.get("tools_invoked", [])],
        "applied_rules": applied_rules,
        "conflicts_detected": state.get("conflicts", []),
        "explanation": state.get("explanation", ""),
        "as_of_date": state["as_of"],
    }
    save_audit(state, response)
    return {"response": response}


def decide_answer_type(state: State) -> str:
    unresolved = any(c.get("unresolved") for c in state.get("conflicts", [])) or \
        any(r["status"] == "conflict" for r in state.get("rules", []))
    if unresolved:
        return "conflict_flagged"
    if state.get("tools_invoked"):
        return "calculated"
    return "retrieved_fact"


def build_citations(state: State) -> list[dict]:
    """Evidence the answer used + the clause of every rule that was applied. No duplicates."""
    citations, seen = [], set()
    by_id = {e["evidence_id"]: e for e in state.get("evidence", [])}
    for eid in state.get("used_evidence", []):
        e = by_id[eid]
        key = (e["doc_id"], e["section"])
        if key not in seen:
            seen.add(key)
            citations.append(citation_for(e["doc_id"], e["section"], e["page"]))
    for r in state.get("rules", []):
        sources = [(r["source_doc_id"], r["source_section"])] if r["source_doc_id"] else []
        sources += [(t["doc_id"], None) for t in r.get("tied", [])]
        for doc_id, section in sources:
            if section is None:  # tied rules: look up their section from the registry
                row = db.query_one("SELECT source_section FROM rule_registry WHERE source_doc_id = ? AND parameter = ?",
                                   (doc_id, r["parameter"]))
                section = row["source_section"] if row else ""
            if (doc_id, section) not in seen:
                seen.add((doc_id, section))
                citations.append(citation_for(doc_id, section))
    return citations


def save_audit(state: State, response: dict) -> None:
    """Audit record (Annex D). No chain-of-thought, no student names or marks beyond tool outputs."""
    record = {
        "trace_id": response["trace_id"],
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "student_id": state.get("student_id"),
        "question": state["question"],
        "question_category": state.get("intent", "unknown"),
        "as_of_date": state["as_of"],
        "sources_retrieved": [{"doc_id": e["doc_id"], "section": e["section"], "score": e["similarity"]}
                              for e in state.get("evidence", [])],
        "precedence_decision": "; ".join(r["decision"] for r in state.get("rules", [])),
        "tools_invoked": [{"tool": t["tool"], "input": t["input"], "output": t["output"], "status": t["status"], "ms": t["ms"]}
                          for t in state.get("tools_invoked", [])],
        "rules_applied": response["applied_rules"],
        "conflicts_detected": response["conflicts_detected"],
        "answer_type": response["answer_type"],
        "model": ", ".join(dict.fromkeys(state.get("models_used", []))) or config.active_model_name(),
        "llm_calls": state.get("llm_calls", 0),
        "llm_fallback_used": state.get("llm_fallback", False),
        "tokens": state.get("tokens", 0),
        "latency_ms": int((time.time() - state["started_at"]) * 1000),
    }
    db.execute(
        "INSERT INTO audit_log (trace_id, timestamp, student_id, question_category, answer_type, record_json) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (record["trace_id"], record["timestamp"], record["student_id"], record["question_category"],
         record["answer_type"], json.dumps(record)),
    )
