// Ask a question. Optional "as of" date lets you see which rule applied on another day.
import { useState } from "react";
import { ask } from "../api.js";
import AnswerCard from "./AnswerCard.jsx";

export default function AskPanel({ session }) {
  const [question, setQuestion] = useState("");
  const [asOfDate, setAsOfDate] = useState("");
  const [history, setHistory] = useState([]); // [{ question, response }] newest first
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    if (!question.trim()) return;
    setError("");
    setLoading(true);
    try {
      const response = await ask(session, question.trim(), asOfDate);
      setHistory([{ question: question.trim(), response }, ...history]);
      setQuestion("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <form className="card ask" onSubmit={submit}>
        <label htmlFor="q">Your question</label>
        <textarea
          id="q"
          rows={3}
          placeholder="e.g. Am I eligible to sit the end-semester exam in Data Structures?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <div className="row">
          <label htmlFor="asof">
            As of date <span className="muted">(optional, default today)</span>
          </label>
          <input id="asof" type="date" value={asOfDate} onChange={(e) => setAsOfDate(e.target.value)} />
          <button className="primary" disabled={loading}>{loading ? "Thinking..." : "Ask"}</button>
        </div>
        {error && <p className="error">{error}</p>}
      </form>

      {history.map((item) => (
        <AnswerCard key={item.response.trace_id} question={item.question} response={item.response} />
      ))}
    </section>
  );
}
