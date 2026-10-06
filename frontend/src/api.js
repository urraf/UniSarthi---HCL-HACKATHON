// All calls to the FastAPI backend live here.
// The backend address comes from frontend/.env (VITE_API_URL), not from the code.
const API_URL = import.meta.env.VITE_API_URL;

// Read the JSON reply; turn HTTP errors into readable messages
async function handle(res) {
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    throw new Error(detail || `Request failed (${res.status})`);
  }
  return data;
}

// Headers for a logged-in student: the guide's X-Student-Id + our login token
function authHeaders(session) {
  if (!session) return {};
  const headers = { Authorization: `Bearer ${session.token}` };
  if (session.role === "student") headers["X-Student-Id"] = session.student_id;
  return headers;
}

// POST helper for JSON bodies
const post = (path, body, session) =>
  fetch(`${API_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...(session ? { Authorization: `Bearer ${session.token}` } : {}) },
    body: JSON.stringify(body),
  }).then(handle);

// ---- Accounts ----
export const login = (rollNumber, password) => post("/login", { roll_number: rollNumber, password });
export const adminLogin = (adminId, password) => post("/admin/login", { admin_id: adminId, password });
export const signupStart = (rollNumber, email) => post("/auth/signup/start", { roll_number: rollNumber, email });
export const signupVerify = (email, otp, password) => post("/auth/signup/verify", { email, otp, password });
export const forgotPassword = (email) => post("/auth/forgot-password", { email });
export const resetPassword = (email, otp, newPassword) =>
  post("/auth/reset-password", { email, otp, new_password: newPassword });
export const forgotRoll = (email) => post("/auth/forgot-roll", { email });

// ---- Chat history ----
export const getHistory = (session) => fetch(`${API_URL}/history`, { headers: authHeaders(session) }).then(handle);
export const clearHistory = (session) =>
  fetch(`${API_URL}/history`, { method: "DELETE", headers: authHeaders(session) }).then(handle);

export function ask(session, question, asOfDate) {
  return fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(session) },
    body: JSON.stringify({ question, as_of_date: asOfDate || null }),
  }).then(handle);
}

// Staff only: upload a document (sends the staff login token)
export function ingest(session, file, metadata) {
  const form = new FormData();
  form.append("file", file);
  form.append("metadata", JSON.stringify(metadata));
  return fetch(`${API_URL}/ingest`, { method: "POST", body: form, headers: authHeaders(session) }).then(handle);
}

export const getMe = (session) =>
  fetch(`${API_URL}/me`, { headers: authHeaders(session) }).then(handle);

export const getSources = () => fetch(`${API_URL}/sources`).then(handle);
export const getAudit = (traceId) => fetch(`${API_URL}/audit/${traceId}`).then(handle);
export const getHealth = () => fetch(`${API_URL}/health`).then(handle);
