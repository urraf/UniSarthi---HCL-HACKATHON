// Upload a new document while the system is running (POST /ingest).
// The form fields are the Source Register fields (Annex B of the guide).
import { useState } from "react";
import { ingest } from "../api.js";

const EMPTY = {
  doc_id: "", title: "", issuer: "", authority_level: 2, doc_type: "circular", version: "1.0",
  effective_from: "", effective_to: "", supersedes: "", scope_programmes: "ALL", scope_batches: "ALL",
  provenance: "", retrieved_on: "", synthetic: "N",
};
const DOC_TYPES = ["regulation", "circular", "notice", "faq", "handbook", "unofficial"];
const LEVELS = { 1: "1 - Statutes, ordinances, regulations", 2: "2 - Official circulars / notifications",
  3: "3 - Department notices", 4: "4 - Handbooks and FAQs", 5: "5 - Unofficial content" };

export default function IngestPanel() {
  const [meta, setMeta] = useState(EMPTY);
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const set = (field) => (e) => setMeta({ ...meta, [field]: e.target.value });

  async function submit(e) {
    e.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);
    try {
      setResult(await ingest(file, { ...meta, authority_level: Number(meta.authority_level) }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form className="card grid-form" onSubmit={submit}>
      <p className="muted full">Add a regulation, circular, notice or FAQ (.pdf, .md, .txt). It is used by the very next question.</p>
      <label className="full">File <input type="file" accept=".pdf,.md,.txt" onChange={(e) => setFile(e.target.files[0])} required /></label>
      <label>Document ID <input value={meta.doc_id} onChange={set("doc_id")} placeholder="ACAD-2026-10" required /></label>
      <label>Title <input value={meta.title} onChange={set("title")} required /></label>
      <label>Issuer <input value={meta.issuer} onChange={set("issuer")} placeholder="Office of the Dean (Academics)" required /></label>
      <label>Authority level
        <select value={meta.authority_level} onChange={set("authority_level")}>
          {Object.entries(LEVELS).map(([v, label]) => <option key={v} value={v}>{label}</option>)}
        </select>
      </label>
      <label>Type
        <select value={meta.doc_type} onChange={set("doc_type")}>
          {DOC_TYPES.map((t) => <option key={t}>{t}</option>)}
        </select>
      </label>
      <label>Version <input value={meta.version} onChange={set("version")} required /></label>
      <label>Effective from <input type="date" value={meta.effective_from} onChange={set("effective_from")} required /></label>
      <label>Effective to <input type="date" value={meta.effective_to} onChange={set("effective_to")} /></label>
      <label>Supersedes <input value={meta.supersedes} onChange={set("supersedes")} placeholder="ACAD-REG-2024#7.2" /></label>
      <label>Programmes <input value={meta.scope_programmes} onChange={set("scope_programmes")} /></label>
      <label>Batches <input value={meta.scope_batches} onChange={set("scope_batches")} placeholder="ALL or 2024+" /></label>
      <label>Provenance (URL) <input value={meta.provenance} onChange={set("provenance")} /></label>
      <div className="full">
        <button className="primary" disabled={loading}>{loading ? "Ingesting..." : "Ingest document"}</button>
      </div>
      {error && <p className="error full">{error}</p>}
      {result && (
        <p className="ok full">
          Indexed {result.doc_id}: {result.chunks_indexed} chunks, {result.rules_added.length} rule(s) added
          {result.rules_added.map((r) => ` · ${r.parameter} ${r.operator} ${r.value} (§${r.source_section})`).join("")}
        </p>
      )}
    </form>
  );
}
