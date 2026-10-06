// Main screen. Not logged in -> AuthScreen.
// Students see only the chat. University staff see "Add document" and "Sources".
import { useState } from "react";
import AuthScreen from "./components/AuthScreen.jsx";
import ChatPanel from "./components/ChatPanel.jsx";
import IngestPanel from "./components/IngestPanel.jsx";
import SourcesPanel from "./components/SourcesPanel.jsx";

const STAFF_TABS = ["Add document", "Sources"];

export default function App() {
  // session = login response: { token, role: "student" | "admin", ... }
  const [session, setSession] = useState(null);
  const [tab, setTab] = useState(STAFF_TABS[0]);

  if (!session) return <AuthScreen onLogin={setSession} />;
  const isStaff = session.role === "admin";

  return (
    <div className="page">
      <header className="topbar">
        <div>
          <h1>UniSarthi</h1>
          <span className="muted">{isStaff ? "Staff: manage university documents" : "Student services assistant"}</span>
        </div>
        <div className="who">
          <strong>{isStaff ? session.admin_id : session.full_name}</strong>
          {!isStaff && (
            <span className="muted">{session.roll_number} · {session.programme} · batch {session.batch_year}</span>
          )}
          <button className="link" onClick={() => setSession(null)}>Log out</button>
        </div>
      </header>

      {isStaff ? (
        <>
          <nav className="tabs">
            {STAFF_TABS.map((t) => (
              <button key={t} className={t === tab ? "tab active" : "tab"} onClick={() => setTab(t)}>{t}</button>
            ))}
          </nav>
          {tab === "Add document" && <IngestPanel session={session} />}
          {tab === "Sources" && <SourcesPanel />}
        </>
      ) : (
        <ChatPanel session={session} />
      )}
    </div>
  );
}
