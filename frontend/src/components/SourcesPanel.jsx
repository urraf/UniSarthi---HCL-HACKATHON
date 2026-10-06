// The Source Register: every ingested document with its authority, version and dates.
import { useEffect, useState } from "react";
import { getSources } from "../api.js";

export default function SourcesPanel() {
  const [docs, setDocs] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getSources().then(setDocs).catch((err) => setError(err.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  return (
    <div className="card table-wrap">
      <table>
        <thead>
          <tr>
            <th>Document</th><th>Issuer</th><th>Level</th><th>Version</th>
            <th>Effective</th><th>Supersedes</th><th>Scope</th><th>Chunks</th>
          </tr>
        </thead>
        <tbody>
          {docs.map((d) => (
            <tr key={d.doc_id}>
              <td><strong>{d.title}</strong><br /><span className="muted">{d.doc_id}{d.synthetic === "Y" ? " · synthetic" : ""}</span></td>
              <td>{d.issuer}</td>
              <td>{d.authority_level}</td>
              <td>{d.version}</td>
              <td>{d.effective_from}{d.effective_to ? ` to ${d.effective_to}` : ""}</td>
              <td>{d.supersedes || "-"}</td>
              <td>{d.scope_programmes} / {d.scope_batches}</td>
              <td>{d.chunks_indexed}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
