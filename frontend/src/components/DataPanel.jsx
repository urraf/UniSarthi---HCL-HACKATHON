// Staff only: read-only view of the database tables, with a search box.
import { useEffect, useState } from "react";
import { getTable } from "../api.js";

const TABLES = { students: "Students", attendance: "Attendance", results: "Results", courses: "Courses", rules: "Rule registry" };

export default function DataPanel({ session }) {
  const [table, setTable] = useState("students");
  const [rows, setRows] = useState([]);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    setError("");
    setRows([]);
    getTable(session, table).then(setRows).catch((err) => setError(err.message));
  }, [session, table]);

  const columns = rows.length ? Object.keys(rows[0]) : [];
  const q = search.trim().toLowerCase();
  const shown = q ? rows.filter((r) => Object.values(r).some((v) => String(v ?? "").toLowerCase().includes(q))) : rows;

  return (
    <div className="card">
      <div className="data-toolbar">
        <div className="mode-tabs">
          {Object.entries(TABLES).map(([key, label]) => (
            <button key={key} className={key === table ? "mode active" : "mode"} onClick={() => setTable(key)}>{label}</button>
          ))}
        </div>
        <input placeholder="Search (roll number, name, course...)" value={search} onChange={(e) => setSearch(e.target.value)} />
        <span className="muted small">{shown.length} of {rows.length} rows · read-only · synthetic data</span>
      </div>
      {error && <p className="error">{error}</p>}
      <div className="table-wrap">
        <table>
          <thead><tr>{columns.map((c) => <th key={c}>{c.replaceAll("_", " ")}</th>)}</tr></thead>
          <tbody>
            {shown.map((r, i) => (
              <tr key={i}>{columns.map((c) => <td key={c}>{r[c] ?? "-"}</td>)}</tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
