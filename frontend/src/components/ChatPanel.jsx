// Chat with the assistant: message bubbles, typing indicator, Enter to send.
// If the assistant asks a follow-up (clarification_needed), the student's short reply
// is joined to the original question, so "Data Structures" answers "Which course?".
import { useEffect, useRef, useState } from "react";
import { ask } from "../api.js";
import Message from "./Message.jsx";

export default function ChatPanel({ session }) {
  const firstName = session.full_name.split(" ")[0];
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: `Hi ${firstName}! I can answer questions about university rules, and check your own attendance, results and eligibility. Ask me anything.`,
    },
  ]);
  const [input, setInput] = useState("");
  const [asOfDate, setAsOfDate] = useState("");
  const [loading, setLoading] = useState(false);
  const [pendingQuestion, setPendingQuestion] = useState(null); // question waiting for a clarification
  const bottomRef = useRef(null);

  // Keep the newest message in view
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text }]);
    setLoading(true);

    // Answering a follow-up question? Combine it with the original question.
    const question = pendingQuestion ? `${pendingQuestion} (${text})` : text;
    try {
      const response = await ask(session, question, asOfDate);
      setPendingQuestion(response.answer_type === "clarification_needed" ? question : null);
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

      <div className="composer">
        <textarea
          rows={1}
          placeholder={pendingQuestion ? "Type your answer..." : "Ask about attendance, exams, placements, fees..."}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={onKeyDown}
          aria-label="Message"
        />
        <button className="primary" onClick={send} disabled={loading || !input.trim()}>Send</button>
      </div>
    </section>
  );
}
