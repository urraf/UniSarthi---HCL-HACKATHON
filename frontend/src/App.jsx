// Main screen. Not logged in -> AuthScreen.
// Students see the chat. University staff see "Student data", "Add document" and "Sources".
// The login is kept in the browser (localStorage) so a page refresh does not log you out;
// on load it is checked with the server (GET /auth/session).
import { useEffect, useState } from "react";
import { checkSession } from "./api.js";
import AuthScreen from "./components/AuthScreen.jsx";
import ChatPanel from "./components/ChatPanel.jsx";
import IngestPanel from "./components/IngestPanel.jsx";
import SourcesPanel from "./components/SourcesPanel.jsx";
import DataPanel from "./components/DataPanel.jsx";

const STAFF_TABS = ["Student data", "Add document", "Sources"];
const STORAGE_KEY = "unisarthi_session";

function loadSaved() {
  try {
    return JSON.parse(localStorage.getItem(STORAGE_KEY));
  } catch {
    return null;
  }
}

export default function App() {
  // session = login response: { token, role: "student" | "admin", ... }
  const [session, setSession] = useState(null);
  const [checking, setChecking] = useState(true);
  const [tab, setTab] = useState(STAFF_TABS[0]);

  // On page load: restore the saved login if the server still accepts its token
  useEffect(() => {
    const saved = loadSaved();
    if (!saved) return setChecking(false);
    checkSession(saved)
      .then(() => setSession(saved))
      .catch(() => logout())
      .finally(() => setChecking(false));
  }, []);

  function login(newSession) {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(newSession));
    } catch {
      /* storage blocked: the login just won't survive a refresh */
    }
    setSession(newSession);
  }

  function logout() {
    try {
      localStorage.removeItem(STORAGE_KEY);
    } catch {
      /* ignore */
    }
    setSession(null);
  }

  if (checking) return <div className="login-wrap"><p className="muted">Loading...</p></div>;
  if (!session) return <AuthScreen onLogin={login} />;
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
          <button className="link" onClick={logout}>Log out</button>
        </div>
      </header>

      {isStaff ? (
        <>
          <nav className="tabs">
            {STAFF_TABS.map((t) => (
              <button key={t} className={t === tab ? "tab active" : "tab"} onClick={() => setTab(t)}>{t}</button>
            ))}
          </nav>
          {tab === "Student data" && <DataPanel session={session} />}
          {tab === "Add document" && <IngestPanel session={session} />}
          {tab === "Sources" && <SourcesPanel />}
        </>
      ) : (
        <ChatPanel session={session} />
      )}
    </div>
  );
}
