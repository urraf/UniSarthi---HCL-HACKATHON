// One chat bubble. Assistant answers also show their type, tools, rules, conflicts and audit (sources are not shown to students).
import { useEffect, useState } from "react";
import { getAudit } from "../api.js";
import FormattedText from "./FormattedText.jsx";

// Friendly labels for the 6 answer types of the guide
const TYPE_LABELS = {
  retrieved_fact: "From documents",
  calculated: "Calculated from your records",
  not_found: "Not found",
  clarification_needed: "Question for you",
  refused: "Refused",
  conflict_flagged: "Sources conflict",
};

// Reveal the text a few characters at a time, like the assistant is typing
function useTypewriter(text, animate) {
  const [shown, setShown] = useState(animate ? "" : text);
  useEffect(() => {
    if (!animate) return;
    let i = 0;
    const timer = setInterval(() => {
      i += 3;
      setShown(text.slice(0, i));
      if (i >= text.length) clearInterval(timer);
    }, 15);
    return () => clearInterval(timer);
  }, [text, animate]);
  return shown;
}

export default function Message({ message }) {
  const { role, text, response, animate, error } = message;
  const shown = useTypewriter(text, animate);
  const done = shown.length >= text.length;

  return (
    <div className={`bubble-row ${role}`}>
      <div className={`bubble ${role}${error ? " error-bubble" : ""}`}>
        {response && <span className={`badge ${response.answer_type}`}>{TYPE_LABELS[response.answer_type]}</span>}
        {role === "assistant" ? (
          <div className="bubble-text"><FormattedText text={shown} /></div>
        ) : (
          <p className="bubble-text">{shown}</p>
        )}
        {response && done && <Details response={response} />}
      </div>
    </div>
  );
}

function Details({ response }) {
  const [audit, setAudit] = useState(null);

  async function toggleAudit() {
    setAudit(audit ? null : await getAudit(response.trace_id));
  }

  return (
    <div className="details">
      {response.explanation && <p className="muted">{response.explanation}</p>}

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
                {c.unresolved
                  ? `Unresolved: ${[].concat(c.unresolved).join(" vs ")}`
                  : `${c.winner} applies over ${[].concat(c.overridden).join(", ")}`}{" "}
                <span className="muted">({c.reason})</span>
              </li>
            ))}
          </ul>
        </details>
      )}

      <div className="meta">
        trace {response.trace_id} · as of {response.as_of_date}
        <button className="link" onClick={toggleAudit}>{audit ? "Hide audit" : "Show audit"}</button>
      </div>
      {audit && <pre>{JSON.stringify(audit, null, 2)}</pre>}
    </div>
  );
}
