// Staff only: look inside ChromaDB. Chunks per document, browse chunks, and a search tester
// that runs the same hybrid search the assistant uses (vector similarity + keyword rank).
import { useEffect, useState } from "react";
import { getVectors } from "../api.js";

export default function VectorPanel({ session }) {
  const [info, setInfo] = useState(null);      // browse result
  const [docId, setDocId] = useState("");
  const [query, setQuery] = useState("");
  const [search, setSearch] = useState(null);  // search result
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setError("");
    getVectors(session, { docId }).then(setInfo).catch((err) => setError(err.message));
  }, [session, docId]);

  async function runSearch(e) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    try {
      setSearch(await getVectors(session, { q: query }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="card">
      {error && <p className="error">{error}</p>}
      {info && (
        <p className="muted small">
          Collection <strong>{info.collection}</strong> · embedding model <strong>{info.model}</strong> ·{" "}
          <strong>{info.total_chunks}</strong> chunks from <strong>{Object.keys(info.chunks_per_document).length}</strong> documents
        </p>
      )}

      <h3>Search test</h3>
      <form className="data-toolbar" onSubmit={runSearch}>
        <input placeholder="Type a question, e.g. minimum attendance required" value={query} onChange={(e) => setQuery(e.target.value)} />
        <button className="primary" disabled={loading}>{loading ? "Searching..." : "Search"}</button>
      </form>
      {search && (
        <div className="table-wrap">
          <table>
            <thead><tr><th>#</th><th>similarity</th><th>keyword rank</th><th>document</th><th>page</th><th>section</th><th>text</th></tr></thead>
            <tbody>
              {search.results.map((r) => (
                <tr key={r.rank}>
                  <td>{r.rank}</td><td>{r.similarity}</td><td>{r.keyword_rank ?? "-"}</td><td>{r.doc_id}</td>
                  <td>{r.page ?? "-"}</td><td>{r.section || "-"}</td><td>{r.text}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {info && (
        <>
          <h3>Chunks per document</h3>
          <div className="mode-tabs">
            <button className={docId === "" ? "mode active" : "mode"} onClick={() => setDocId("")}>All</button>
            {Object.entries(info.chunks_per_document).map(([d, n]) => (
              <button key={d} className={d === docId ? "mode active" : "mode"} onClick={() => setDocId(d)}>{d} ({n})</button>
            ))}
          </div>
          <p className="muted small">Showing {info.chunks.length} chunks{docId ? ` of ${docId}` : " (first 50)"}.</p>
          <div className="table-wrap">
            <table>
              <thead><tr><th>chunk id</th><th>document</th><th>page</th><th>section</th><th>authority</th><th>effective</th><th>text</th></tr></thead>
              <tbody>
                {info.chunks.map((c) => (
                  <tr key={c.id}>
                    <td>{c.id}</td><td>{c.doc_id}</td><td>{c.page ?? "-"}</td><td>{c.section || "-"}</td>
                    <td>{c.authority_level}</td><td>{c.effective_from}</td><td>{c.text}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
