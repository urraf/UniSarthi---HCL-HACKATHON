// Main screen: login first, then three tabs (Chat, Upload document, Sources).
import { useState } from "react";
import Login from "./components/Login.jsx";
import ChatPanel from "./components/ChatPanel.jsx";
import IngestPanel from "./components/IngestPanel.jsx";
import SourcesPanel from "./components/SourcesPanel.jsx";

const TABS = ["Chat", "Upload document", "Sources"];

export default function App() {
  // session = { token, student_id, full_name, programme, batch_year } after login
  const [session, setSession] = useState(null);
  const [tab, setTab] = useState(TABS[0]);

  if (!session) return <Login onLogin={setSession} />;

  return (
    <div className="page">
      <header className="topbar">
        <div>
          <h1>UniSarthi</h1>
          <span className="muted">Student services assistant</span>
        </div>
        <div className="who">
          <strong>{session.full_name}</strong>
          <span className="muted">
            {session.student_id} · {session.programme} · batch {session.batch_year}
          </span>
          <button className="link" onClick={() => setSession(null)}>Log out</button>
        </div>
      </header>

      <nav className="tabs">
        {TABS.map((t) => (
          <button key={t} className={t === tab ? "tab active" : "tab"} onClick={() => setTab(t)}>{t}</button>
        ))}
      </nav>

      {tab === "Chat" && <ChatPanel session={session} />}
      {tab === "Upload document" && <IngestPanel />}
      {tab === "Sources" && <SourcesPanel />}
    </div>
  );
}
