// Shows one answer: type badge, answer, explanation, citations, tools, rules, conflicts, audit.
import { useState } from "react";
import { getAudit } from "../api.js";

// Friendly labels for the 6 answer types of the guide
const TYPE_LABELS = {
  retrieved_fact: "From documents",
  calculated: "Calculated from your records",
  not_found: "Not found",
  clarification_needed: "Needs clarification",
  refused: "Refused",
  conflict_flagged: "Sources conflict",
};

export default function AnswerCard({ question, response }) {
  const [audit, setAudit] = useState(null);

  async function toggleAudit() {
    setAudit(audit ? null : await getAudit(response.trace_id));
  }

  return (
    <article className="card answer">
      <p className="question">{question}</p>
      <span className={`badge ${response.answer_type}`}>{TYPE_LABELS[response.answer_type]}</span>
      <p className="answer-text">{response.answer}</p>
      {response.explanation && <p className="muted">{response.explanation}</p>}

      {response.citations.length > 0 && (
        <details open>
          <summary>Sources ({response.citations.length})</summary>
          <ul>
            {response.citations.map((c) => (
              <li key={`${c.doc_id}-${c.section}`}>
                <strong>{c.title}</strong> ({c.doc_id}) · section {c.section}
                {c.page ? ` · page ${c.page}` : ""} · version {c.version} · effective {c.effective_from}
              </li>
            ))}
          </ul>
        </details>
      )}

      {response.tools_invoked.length > 0 && (
        <details>
          <summary>Tools used ({response.tools_invoked.length})</summary>
          {response.tools_invoked.map((t, i) => (
            <pre key={i}>{t.tool}({JSON.stringify(t.input)}){"\n"}→ {JSON.stringify(t.output, null, 1)}</pre>
          ))}
        </details>
      )}

      {response.applied_rules.length > 0 && (
        <details>
          <summary>Rules applied ({response.applied_rules.length})</summary>
          <ul>
            {response.applied_rules.map((r) => (
              <li key={r.rule_id}>{r.rule_id}: {r.parameter} {r.value} ({r.source_doc_id} §{r.source_section})</li>
            ))}
          </ul>
        </details>
      )}

      {response.conflicts_detected.length > 0 && (
        <details>
          <summary>Conflicts resolved ({response.conflicts_detected.length})</summary>
          <ul>
            {response.conflicts_detected.map((c, i) => (
              <li key={i}>
                {c.unresolved ? `Unresolved: ${[].concat(c.unresolved).join(" vs ")}` : `${c.winner} applies over ${[].concat(c.overridden).join(", ")}`}
                {" "}<span className="muted">({c.reason})</span>
              </li>
            ))}
          </ul>
        </details>
      )}

      <footer className="meta">
        trace {response.trace_id} · as of {response.as_of_date}
        <button className="link" onClick={toggleAudit}>{audit ? "Hide audit" : "Show audit"}</button>
      </footer>
      {audit && <pre>{JSON.stringify(audit, null, 2)}</pre>}
    </article>
  );
}
