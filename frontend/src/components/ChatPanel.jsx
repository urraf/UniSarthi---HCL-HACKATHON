// Chat with the assistant: message bubbles, typing indicator, Enter to send.
// If the assistant asks a follow-up (clarification_needed), the student's short reply
// is joined to the original question, so "Data Structures" answers "Which course?".
import { useEffect, useRef, useState } from "react";
import { ask, clearHistory, getHistory, getMe } from "../api.js";
import { buildSuggestions } from "../suggestions.js";
import Message from "./Message.jsx";

export default function ChatPanel({ session }) {
  const firstName = session.full_name.split(" ")[0];
  const greeting = {
    role: "assistant",
    text: `Hi ${firstName}! I can answer questions about university rules, and check your own attendance, results and eligibility. Ask me anything.`,
  };
  const [messages, setMessages] = useState([greeting]);
  const [input, setInput] = useState("");
  const [asOfDate, setAsOfDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [pendingQuestion, setPendingQuestion] = useState(null); // question waiting for a clarification
  const [suggestions, setSuggestions] = useState([]);
  const bottomRef = useRef(null);

  // Load the saved chat history (MongoDB) after login
  useEffect(() => {
    getHistory(session)
      .then((saved) => setMessages([greeting, ...saved.map((m) => ({ role: m.role, text: m.text, response: m.response }))]))
      .catch(() => {});
  }, [session]); // eslint-disable-line react-hooks/exhaustive-deps

  async function clearChat() {
    await clearHistory(session);
    setMessages([greeting]);
    setPendingQuestion(null);
  }

  // Suggested questions use the student's own courses (from GET /me)
  useEffect(() => {
    getMe(session)
      .then((me) => setSuggestions(buildSuggestions(me.courses)))
      .catch(() => setSuggestions(buildSuggestions([])));
  }, [session]);

  // Keep the newest message in view
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // Send the typed message, or a suggested question when a chip is clicked
  async function send(chipText) {
    const text = (chipText ?? input).trim();
    if (!text || loading) return;
    if (!chipText) setInput("");
    setMessages((m) => [...m, { role: "user", text }]);
    setLoading(true);

    // A short reply to the assistant's follow-up question ("Which course?") is combined with
    // the original question. A full new question is sent on its own.
    const isShortReply = text.split(/\s+/).length <= 6;
    const question = pendingQuestion && !chipText && isShortReply ? `${pendingQuestion} (${text})` : text;
    try {
      const response = await ask(session, question, asOfDate);
      // Remember the question only if the assistant asked a real follow-up (not a small-talk reply)
      const askedFollowUp = response.answer_type === "clarification_needed" && !response.explanation.startsWith("Small talk");
      setPendingQuestion(askedFollowUp ? question : null);
      setMessages((m) => [...m, { role: "assistant", text: response.answer, response, animate: true }]);
    } catch (err) {
      setPendingQuestion(null);
      setMessages((m) => [...m, { role: "assistant", text: `Sorry, something went wrong: ${err.message}`, error: true }]);
    } finally {
      setLoading(false);
    }
  }

  // Enter sends, Shift+Enter makes a new line
  function onKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send();
    }
  }

  return (
    <section className="chat">
      <div className="chat-options">
        <label htmlFor="asof">Answer as of</label>
        <input id="asof" type="date" value={asOfDate} onChange={(e) => setAsOfDate(e.target.value)} />
        <span className="muted">{asOfDate ? "" : "today"}</span>
        <button className="link clear" onClick={clearChat} disabled={loading}>Clear chat</button>
      </div>

      <div className="messages">
        {messages.map((m, i) => (
          <Message key={i} message={m} />
        ))}
        {loading && (
          <div className="bubble-row assistant">
            <div className="bubble assistant typing" aria-label="Assistant is typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {suggestions.length > 0 && (
        <div className="suggestions" aria-label="Suggested questions">
          {suggestions.map((q) => (
            <button key={q} className="chip" onClick={() => send(q)} disabled={loading}>{q}</button>
          ))}
        </div>
      )}

      <div className="composer">
        <textarea
          rows={1}
          placeholder={pendingQuestion ? "Type your answer..." : "Ask about attendance, exams, placements, fees..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          aria-label="Message"
        />
        <button className="primary" onClick={() => send()} disabled={loading || !input.trim()}>Send</button>
      </div>
    </section>
  );
}
