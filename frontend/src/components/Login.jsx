// Login with student ID + password. The backend returns a signed token.
import { useState } from "react";
import { login } from "../api.js";

export default function Login({ onLogin }) {
  const [studentId, setStudentId] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      onLogin(await login(studentId.trim().toUpperCase(), password));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="login-wrap">
      <form className="card login" onSubmit={submit}>
        <h1>UniSarthi</h1>
        <p className="muted">Log in with your student ID to ask about rules, attendance, results and eligibility.</p>
        <label htmlFor="sid">Student ID</label>
        <input id="sid" placeholder="S1001" value={studentId} onChange={(e) => setStudentId(e.target.value)} required />
        <label htmlFor="pw">Password</label>
        <input id="pw" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        {error && <p className="error">{error}</p>}
        <button className="primary" disabled={loading}>{loading ? "Logging in..." : "Log in"}</button>
      </form>
    </div>
  );
}
