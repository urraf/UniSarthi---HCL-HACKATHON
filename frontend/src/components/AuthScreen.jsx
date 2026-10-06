// Everything before login: student login, create account (email OTP), forgot password,
// forgot roll number, and staff login. One small form per mode.
import { useState } from "react";
import * as api from "../api.js";

const MODES = {
  login: "Student login",
  signup: "Create account",
  forgot: "Forgot password",
  roll: "Forgot roll number",
  staff: "Staff login",
};

export default function AuthScreen({ onLogin }) {
  const [mode, setMode] = useState("login");
  const [f, setF] = useState({ roll: "", email: "", password: "", otp: "", staffId: "" });
  const [otpSent, setOtpSent] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const set = (key) => (e) => setF({ ...f, [key]: e.target.value });

  function switchMode(next) {
    setMode(next);
    setOtpSent(false);
    setMessage("");
    setError("");
  }

  // Run one API call with loading + error handling
  async function run(action) {
    setError("");
    setMessage("");
    setLoading(true);
    try {
      await action();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function submit(e) {
    e.preventDefault();
    const roll = f.roll.trim().toUpperCase();
    const email = f.email.trim().toLowerCase();

    if (mode === "login") return run(async () => onLogin(await api.login(roll, f.password)));
    if (mode === "staff") return run(async () => onLogin(await api.adminLogin(f.staffId.trim(), f.password)));
    if (mode === "roll") return run(async () => setMessage((await api.forgotRoll(email)).message));

    if (mode === "signup") {
      return run(async () => {
        if (!otpSent) {
          setMessage((await api.signupStart(roll, email)).message);
          setOtpSent(true);
        } else {
          await api.signupVerify(email, f.otp.trim(), f.password);
          switchMode("login");
          setMessage("Account created. Log in with your roll number.");
        }
      });
    }
    if (mode === "forgot") {
      return run(async () => {
        if (!otpSent) {
          setMessage((await api.forgotPassword(email)).message);
          setOtpSent(true);
        } else {
          await api.resetPassword(email, f.otp.trim(), f.password);
          switchMode("login");
          setMessage("Password changed. Log in with your new password.");
        }
      });
    }
  }

  const buttonText = {
    login: "Log in",
    staff: "Log in as staff",
    roll: "Email my roll number",
    signup: otpSent ? "Create account" : "Send code to my email",
    forgot: otpSent ? "Set new password" : "Send code to my email",
  }[mode];

  return (
    <div className="login-wrap">
      <form className="card login" onSubmit={submit}>
        <h1>UniSarthi</h1>
        <p className="muted">Your university services assistant</p>

        <div className="mode-tabs">
          {Object.entries(MODES).map(([key, label]) => (
            <button type="button" key={key} className={key === mode ? "mode active" : "mode"} onClick={() => switchMode(key)}>
              {label}
            </button>
          ))}
        </div>

        {(mode === "login" || mode === "signup") && (
          <label>Roll number <input value={f.roll} onChange={set("roll")} placeholder="2023UIT3015" required disabled={otpSent} /></label>
        )}
        {mode === "staff" && <label>Staff ID <input value={f.staffId} onChange={set("staffId")} required /></label>}
        {(mode === "signup" || mode === "forgot" || mode === "roll") && (
          <label>University email <input type="email" value={f.email} onChange={set("email")} placeholder="name@nsut.ac.in" required disabled={otpSent} /></label>
        )}
        {otpSent && <label>Code from your email <input value={f.otp} onChange={set("otp")} inputMode="numeric" maxLength={6} required /></label>}
        {(mode === "login" || mode === "staff" || otpSent) && (
          <label>
            {otpSent ? "New password (min 8 characters)" : "Password"}
            <input type="password" value={f.password} onChange={set("password")} required minLength={otpSent ? 8 : 1} />
          </label>
        )}

        {message && <p className="ok">{message}</p>}
        {error && <p className="error">{error}</p>}
        <button className="primary" disabled={loading}>{loading ? "Please wait..." : buttonText}</button>
      </form>
    </div>
  );
}
