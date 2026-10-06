// Chat with the assistant, with saved chats (MongoDB) in a side list.
// - "New chat" starts an empty conversation; the first question creates it on the server.
// - Clicking a chat in the list loads its messages.
// - If the assistant asks a follow-up ("Which course?"), a short reply is joined to the original question.
import { useEffect, useRef, useState } from "react";
import { ask, deleteChat, getChat, getMe, listChats } from "../api.js";
import { buildSuggestions } from "../suggestions.js";
import Message from "./Message.jsx";

export default function ChatPanel({ session }) {
  const firstName = session.full_name.split(" ")[0];
  const greeting = {
    role: "assistant",
    text: `Hi ${firstName}! I can answer questions about university rules, and check your own attendance, results and eligibility. Ask me anything.`,
  };
  const [chats, setChats] = useState([]);           // saved conversations, newest first
  const [chatId, setChatId] = useState(null);       // open conversation (null = new chat)
  const [messages, setMessages] = useState([greeting]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [pendingQuestion, setPendingQuestion] = useState(null); // question waiting for a clarification
  const [suggestions, setSuggestions] = useState([]);
  const bottomRef = useRef(null);

  const refreshChats = () => listChats(session).then(setChats).catch(() => {});

  // On login: saved chats + suggested questions (from the student's own courses)
  useEffect(() => {
    refreshChats();
    getMe(session)
      .then((me) => setSuggestions(buildSuggestions(me)))
      .catch(() => setSuggestions(buildSuggestions({})));
  }, [session]); // eslint-disable-line react-hooks/exhaustive-deps

  // Keep the newest message in view
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function newChat() {
    setChatId(null);
    setMessages([greeting]);
    setPendingQuestion(null);
  }

  async function openChat(id) {
    const saved = await getChat(session, id);
    setChatId(id);
    setPendingQuestion(null);
    setMessages([greeting, ...saved.map((m) => ({ role: m.role, text: m.text, response: m.response }))]);
  }

  async function removeChat(id) {
    await deleteChat(session, id);
    if (id === chatId) newChat();
    refreshChats();
  }

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
      const response = await ask(session, question, chatId);
      // Remember the question only if the assistant asked a real follow-up (not a small-talk reply)
      const askedFollowUp = response.answer_type === "clarification_needed" && !response.explanation.startsWith("Small talk");
      setPendingQuestion(askedFollowUp ? question : null);
      setMessages((m) => [...m, { role: "assistant", text: response.answer, response, animate: true }]);
      if (response.conversation_id && response.conversation_id !== chatId) {
        setChatId(response.conversation_id); // the server created this chat
      }
      refreshChats();
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
    <div className="chat-layout">
      <aside className="chat-list" aria-label="Your chats">
        <button className="primary new-chat" onClick={newChat} disabled={loading}>+ New chat</button>
        {chats.length === 0 && <p className="muted small">Your chats will appear here.</p>}
        {chats.map((c) => (
          <div key={c.conversation_id} className={c.conversation_id === chatId ? "chat-item active" : "chat-item"}>
            <button className="chat-title" onClick={() => openChat(c.conversation_id)} disabled={loading} title={c.title}>
              {c.title}
            </button>
            <button className="chat-delete" onClick={() => removeChat(c.conversation_id)} aria-label="Delete chat">×</button>
          </div>
        ))}
      </aside>

      <section className="chat">
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
    </div>
  );
}
