"""
Source Precedence Policy (Annex A of the guide), written as plain code.

When documents (or rules taken from documents) disagree , we decide the winner in 5 steps:
  1. Applicability   - only items in force on as_of_date and in scope for this student
  2. Supersession    - an item explicitly replaced by a level 1 or 2 document is removed
  3. Authority       - lower level number wins (1 = regulations ... 5 = unofficial)
  4. Recency         - same authority: later effective_from wins
  5. Unresolved      - still a tie with different values: report a conflict, cite both

Level 5 (unofficial) content may be shown as information but never wins.

An "item" is a dict with at least:
  doc_id, section, authority_level, effective_from, effective_to,
  supersedes, scope_programmes, scope_batches
and optionally "value" (for rules) and "label" (rule_id or chunk id, for messages).
The same function works for rule rows (tools) and for document chunks (text answers).
"""


def _split(text: str | None) -> list[str]:
    """'A; B,C' -> ['A', 'B', 'C']"""
    return [p.strip() for p in (text or "").replace(",", ";").split(";") if p.strip()]


def is_effective(item: dict, as_of: str) -> bool:
    """In force on as_of (dates are YYYY-MM-DD strings, so text comparison works)."""
    starts_ok = item["effective_from"] <= as_of
    ends_ok = not item.get("effective_to") or item["effective_to"] >= as_of
    return starts_ok and ends_ok


def covers(item: dict, student: dict | None) -> bool:
    """Does the item's programme/batch scope include this student? General questions (no student) see everything."""
    if student is None:
        return True
    programmes = _split(item.get("scope_programmes")) or ["ALL"]
    # "B.Tech" covers "B.Tech IT" and "B.Tech CSE"
    if "ALL" not in programmes and not any(student["programme"] == p or student["programme"].startswith(p + " ")
                                           for p in programmes):
        return False
    batches = _split(item.get("scope_batches")) or ["ALL"]
    if "ALL" in batches:
        return True
    for b in batches:
        if b.endswith("+") and student["batch_year"] >= int(b[:-1]):  # e.g. "2024+"
            return True
        if b.isdigit() and student["batch_year"] == int(b):
            return True
    return False


def clause_ref(item: dict) -> str:
    """'ACAD-REG-2024#7.2' - the form used in the supersedes column."""
    return f"{item['doc_id']}#{item['section']}"


def name(item: dict) -> str:
    return item.get("label") or clause_ref(item)


def resolve(items: list[dict], student: dict | None, as_of: str) -> dict:
    """
    Apply the 5 steps and return:
      status:     "resolved" | "conflict" | "none"
      winner:     the item that applies (or None)
      tied:       items in an unresolved conflict
      overridden: [{"item": ..., "reason": ...}]  items that lost, and why
      upcoming:   items not yet in force (mention as upcoming changes)
      decision:   one-line explanation for the audit / answer
    """
    overridden = []

    # Step 1: applicability
    upcoming = [i for i in items if i["effective_from"] > as_of and covers(i, student)]
    live = [i for i in items if is_effective(i, as_of) and covers(i, student)]

    # Step 2: explicit supersession (only documents of authority 1 or 2 can supersede)
    replaced_by = {}
    for i in live:
        if i["authority_level"] <= 2:
            for ref in _split(i.get("supersedes")):
                replaced_by[ref] = i
    still_live = []
    for i in live:
        by = replaced_by.get(clause_ref(i)) or replaced_by.get(i["doc_id"])
        if by is not None and by is not i:
            overridden.append({"item": i, "reason": f"superseded by {by['doc_id']} (step 2: supersession)"})
        else:
            still_live.append(i)
    live = still_live

    # Level 5 never overrides anything
    official = [i for i in live if i["authority_level"] < 5]
    for i in live:
        if i["authority_level"] >= 5:
            overridden.append({"item": i, "reason": "unofficial source, informational only (level 5)"})

    if not official:
        return {"status": "none", "winner": None, "tied": [], "overridden": overridden,
                "upcoming": upcoming, "decision": "No applicable official source."}

    # Step 3: highest authority (lowest number)
    top_level = min(i["authority_level"] for i in official)
    # Step 4: most recent among the highest authority
    top = [i for i in official if i["authority_level"] == top_level]
    newest = max(i["effective_from"] for i in top)
    winners = [i for i in top if i["effective_from"] == newest]

    for i in official:
        if i in winners:
            continue
        if i["authority_level"] > top_level:
            reason = f"lower authority (level {i['authority_level']} vs {top_level}) (step 3: authority)"
        else:
            reason = f"older (effective {i['effective_from']} vs {newest}) (step 4: recency)"
        overridden.append({"item": i, "reason": reason})

    # Step 5: still several winners that disagree -> unresolved conflict
    values = {str(w.get("value", "")) for w in winners}
    if len(winners) > 1 and len(values) > 1:
        return {"status": "conflict", "winner": None, "tied": winners, "overridden": overridden,
                "upcoming": upcoming,
                "decision": "Unresolved conflict between " + " and ".join(name(w) for w in winners) + " (step 5)"}

    winner = winners[0]
    if overridden:
        decision = f"{name(winner)} applies; " + "; ".join(f"{name(o['item'])} {o['reason']}" for o in overridden)
    else:
        decision = f"{name(winner)} applies (no conflict)"
    return {"status": "resolved", "winner": winner, "tied": [], "overridden": overridden,
            "upcoming": upcoming, "decision": decision}
