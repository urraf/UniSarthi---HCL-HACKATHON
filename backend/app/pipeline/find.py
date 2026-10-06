"""
Step 3 - Find the evidence (no LLM).

1. Hybrid search (ChromaDB vectors + BM25 keywords) with the question and the LLM's rewritten search query.
2. Keep only chunks in force on as_of_date and in scope for this student (precedence step 1).
   Not-yet-effective documents are kept aside as "upcoming".
3. Drop chunks whose clause was superseded by a level 1-2 document (precedence step 2).
4. Keep the most relevant chunks, then order them: higher authority first, then newer (steps 3-4).
5. Resolve the rules the question is about (rule registry + precedence policy).
6. Nothing in force? Use matching EXPIRED documents, clearly labelled as no longer in force.
7. Nothing relevant at all for a policy question -> not_found (R3).
"""
from app import config, db, tools, vectors
from app.precedence import clause_ref, covers, is_effective
from app.pipeline.state import State


def find(state: State) -> dict:
    student, as_of = state.get("student"), state["as_of"]

    # Search with the original question and the LLM's rewritten search query; keep each chunk's best score
    best = {}
    for query in {state["question"], state.get("search_query") or state["question"]}:
        for h in vectors.hybrid_search(query, k=config.TOP_K * 3):
            if h["id"] not in best or h["similarity"] > best[h["id"]]["similarity"]:
                best[h["id"]] = h
    # Relevant enough: close in meaning, or a top keyword match that is still reasonably close
    hits = [h for h in best.values() if h["similarity"] >= config.MIN_SIMILARITY
            or (h.get("keyword_rank", 99) <= 3 and h["similarity"] >= config.MIN_SIMILARITY - 0.1)]

    upcoming = [h for h in hits if h["effective_from"] > as_of and covers(h, student)]
    live = [h for h in hits if is_effective(h, as_of) and covers(h, student)]

    replaced = superseded_refs(student, as_of)
    live = [h for h in live if h["doc_id"] not in replaced and clause_ref(h) not in replaced]

    # Keep the TOP_K most relevant chunks, THEN order them by precedence for the LLM
    evidence = sorted(live, key=lambda h: (-h["similarity"] - (0.05 if h.get("keyword_rank", 99) <= 3 else 0)))[: config.TOP_K]
    evidence.sort(key=lambda h: (h["authority_level"], _neg_date(h["effective_from"]), -h["similarity"]))
    for i, e in enumerate(evidence, start=1):
        e["evidence_id"] = f"E{i}"

    # Nothing in force, but an EXPIRED document matches (e.g. the 2024-25 placement policy):
    # use it as clearly-labelled background so the student hears what the last rule said and that it expired.
    if not evidence:
        expired = [h for h in hits if h.get("effective_to") and h["effective_to"] < as_of and covers(h, student)]
        evidence = sorted(expired, key=lambda h: -h["similarity"])[: config.TOP_K]
        for e in evidence:
            e["expired"] = True
        for i, e in enumerate(evidence, start=1):
            e["evidence_id"] = f"E{i}"

    rules = [tools.get_rule(p, student, as_of) for p in state.get("rule_parameters", [])]

    out = {"evidence": evidence, "upcoming": _one_per_doc(upcoming), "rules": rules}
    if not evidence and state["intent"] == "policy":
        out.update({"stop": True, "answer_type": "not_found", "answer": config.NOT_FOUND_MESSAGE,
                    "explanation": "No authorised document passage was relevant enough to answer. "
                                   "Try asking about attendance, exams, supplementary exams, grades, placements or fees."})
    return out


def superseded_refs(student: dict | None, as_of: str) -> set[str]:
    """Every 'DOC' or 'DOC#clause' replaced by a level 1-2 document that is in force for this student."""
    refs = set()
    for d in db.query("SELECT * FROM documents WHERE authority_level <= 2 AND supersedes != ''"):
        if is_effective(d, as_of) and covers(d, student):
            refs.update(r.strip() for r in d["supersedes"].split(";") if r.strip())
    return refs


def citation_for(doc_id: str, section: str, page=None) -> dict:
    """Build a citation from document metadata (never from LLM text)."""
    doc = db.query_one("SELECT title, version, effective_from FROM documents WHERE doc_id = ?", (doc_id,)) or {}
    if page is None:
        found = vectors.collection().get(where={"$and": [{"doc_id": doc_id}, {"section": section}]}, limit=1)
        page = found["metadatas"][0]["page"] if found["ids"] else None
    return {"doc_id": doc_id, "title": doc.get("title", ""), "section": section, "page": page,
            "version": doc.get("version", ""), "effective_from": doc.get("effective_from", "")}


def _neg_date(date: str) -> int:
    """Turn '2026-08-01' into -20260801 so that newer dates sort first."""
    return -int(date.replace("-", ""))


def _one_per_doc(items: list[dict]) -> list[dict]:
    seen, out = set(), []
    for i in items:
        if i["doc_id"] not in seen:
            seen.add(i["doc_id"])
            out.append({"doc_id": i["doc_id"], "title": i["title"], "effective_from": i["effective_from"]})
    return out
