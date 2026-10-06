"""
Evaluation: run every question in questions.json against the LIVE API and measure the results.

Method (stated as the guide asks): automatic exact / keyword matching, no LLM judge.
  - Answer correctness:     answer_type matches AND expected keywords appear (exact values for numbers)
                            AND forbidden phrases do not appear AND the expected tool result matches
  - Citation accuracy:      the expected document (and section, if given) is among the citations
  - Abstention accuracy:    not_found exactly when expected (answerable questions must NOT abstain)
  - Tool-result correctness: the named tool's output field equals the expected value
  - Retrieval hit rate@k:   the expected document is among the chunks retrieved (from the audit record)
  - Latency and cost:       p50 / p95 latency, LLM calls and tokens per question (from the audit record)

Run (API must be running):  python eval/run_eval.py [--api http://localhost:8000] [--label my-config] [--pause 8]
Writes eval/report_<label>.md and eval/results_<label>.json
"""
import argparse
import json
import statistics
import time
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent


def ask(api: str, q: dict) -> dict:
    headers = {"X-Student-Id": q["student_id"]} if q.get("student_id") else {}
    resp = requests.post(f"{api}/ask", json={"question": q["question"], "as_of_date": q.get("as_of_date")},
                         headers=headers, timeout=180)
    resp.raise_for_status()
    response = resp.json()
    audit = requests.get(f"{api}/audit/{response['trace_id']}", timeout=30).json()
    return {"response": response, "audit": audit}


def tool_value(response: dict, tool: str, field: str):
    for t in response["tools_invoked"]:
        if t["tool"] == tool:
            out = t["output"][0] if isinstance(t["output"], list) and t["output"] else t["output"]
            return out.get(field) if isinstance(out, dict) else None
    return None


def score(q: dict, response: dict, audit: dict) -> dict:
    text = (response["answer"] + " " + response["explanation"]).lower()
    checks = {"type_ok": response["answer_type"] == q["expected_type"]}
    checks["keywords_ok"] = all(k.lower() in text for k in q.get("expect_contains", []))
    checks["forbidden_ok"] = not any(k.lower() in response["answer"].lower() for k in q.get("must_not_contain", []))

    if "expected_tool" in q:
        t = q["expected_tool"]
        checks["tool_ok"] = tool_value(response, t["tool"], t["field"]) == t["value"]
    if "expected_doc" in q:
        cited = {(c["doc_id"], c["section"]) for c in response["citations"]}
        checks["citation_ok"] = any(d == q["expected_doc"] and (not q.get("expected_section") or s == q["expected_section"])
                                    for d, s in cited)
        checks["retrieval_hit"] = q["expected_doc"] in {s["doc_id"] for s in audit["sources_retrieved"]} or \
            q["expected_doc"] in {r["source_doc_id"] for r in response["applied_rules"]}
    checks["correct"] = checks["type_ok"] and checks["keywords_ok"] and checks["forbidden_ok"] and checks.get("tool_ok", True)
    checks["abstention_ok"] = (response["answer_type"] == "not_found") == (q["expected_type"] == "not_found")
    return checks


def pct(values: list[bool]) -> str:
    return f"{100 * sum(values) / len(values):.0f}% ({sum(values)}/{len(values)})" if values else "n/a"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://localhost:8000")
    parser.add_argument("--label", default="default")
    parser.add_argument("--pause", type=float, default=8, help="seconds between questions (Groq free tier: 8000 tokens/min)")
    args = parser.parse_args()

    questions = json.loads((HERE / "questions.json").read_text())
    rows = []
    for i, q in enumerate(questions):
        if i:
            time.sleep(args.pause)
        result = ask(args.api, q)
        checks = score(q, result["response"], result["audit"])
        rows.append({"id": q["id"], "category": q["category"], "question": q["question"],
                     "expected_type": q["expected_type"], "got_type": result["response"]["answer_type"],
                     "answer": result["response"]["answer"], "checks": checks,
                     "latency_ms": result["audit"]["latency_ms"], "llm_calls": result["audit"]["llm_calls"],
                     "tokens": result["audit"]["tokens"], "trace_id": result["response"]["trace_id"]})
        print(f"{q['id']:3} {'PASS' if checks['correct'] else 'FAIL'}  {result['response']['answer_type']:20} {q['question'][:60]}")

    latencies = sorted(r["latency_ms"] for r in rows)
    metrics = {
        "Answer correctness": pct([r["checks"]["correct"] for r in rows]),
        "Citation accuracy": pct([r["checks"]["citation_ok"] for r in rows if "citation_ok" in r["checks"]]),
        "Abstention accuracy": pct([r["checks"]["abstention_ok"] for r in rows]),
        "Tool-result correctness": pct([r["checks"]["tool_ok"] for r in rows if "tool_ok" in r["checks"]]),
        "Retrieval hit rate@k": pct([r["checks"]["retrieval_hit"] for r in rows if "retrieval_hit" in r["checks"]]),
        "Latency p50 / p95 (ms)": f"{statistics.median(latencies):.0f} / {latencies[int(0.95 * (len(latencies) - 1))]}",
        "LLM calls per question (avg)": f"{statistics.mean(r['llm_calls'] for r in rows):.2f}",
        "Tokens per question (avg)": f"{statistics.mean(r['tokens'] for r in rows):.0f}",
    }

    (HERE / f"results_{args.label}.json").write_text(json.dumps({"metrics": metrics, "rows": rows}, indent=2))
    lines = [f"# Evaluation report ({args.label})", "",
             f"{len(rows)} questions, run against the live API. Method: automatic exact/keyword matching (see run_eval.py).", "",
             "| Metric | Result |", "|---|---|", *[f"| {k} | {v} |" for k, v in metrics.items()], "",
             "| ID | Category | Expected | Got | Correct | Question |", "|---|---|---|---|---|---|",
             *[f"| {r['id']} | {r['category']} | {r['expected_type']} | {r['got_type']} | {'yes' if r['checks']['correct'] else 'NO'} | {r['question']} |" for r in rows]]
    (HERE / f"report_{args.label}.md").write_text("\n".join(lines) + "\n")
    print("\n" + "\n".join(f"{k}: {v}" for k, v in metrics.items()))


if __name__ == "__main__":
    main()
