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
  return session ? { "X-Student-Id": session.student_id, Authorization: `Bearer ${session.token}` } : {};
}

export function login(studentId, password) {
  return fetch(`${API_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ student_id: studentId, password }),
  }).then(handle);
}

export function ask(session, question, asOfDate) {
  return fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders(session) },
    body: JSON.stringify({ question, as_of_date: asOfDate || null }),
  }).then(handle);
}

export function ingest(file, metadata) {
  const form = new FormData();
  form.append("file", file);
  form.append("metadata", JSON.stringify(metadata));
  return fetch(`${API_URL}/ingest`, { method: "POST", body: form }).then(handle);
}

export const getMe = (session) =>
  fetch(`${API_URL}/me`, { headers: authHeaders(session) }).then(handle);

export const getSources = () => fetch(`${API_URL}/sources`).then(handle);
export const getAudit = (traceId) => fetch(`${API_URL}/audit/${traceId}`).then(handle);
export const getHealth = () => fetch(`${API_URL}/health`).then(handle);
