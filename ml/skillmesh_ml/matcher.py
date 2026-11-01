"""Step 4: ranking. This is the function the backend calls: get_top_matches(me, candidates, n)."""
from .scoring import score_pair


def get_top_matches(me: dict, candidates: list[dict], n: int = 10, weights: dict | None = None) -> list[dict]:
    """Return the n best peers as [{user_id, score, parts, reasons}], highest score first."""
    results = []
    for peer in candidates:
        if peer["id"] == me["id"]:
            continue
        results.append({"user_id": peer["id"], **score_pair(me, peer, weights)})
    results.sort(key=lambda r: (-r["score"], str(r["user_id"])))
    return results[:n]


def keyword_top(me: dict, candidates: list[dict], n: int = 10) -> list[dict]:
    """Baseline for the report: plain exact-keyword search."""
    out = []
    for peer in candidates:
        if peer["id"] == me["id"]:
            continue
        offered = {x.lower().strip() for x in peer["offered"]}
        hits = sum(1 for w in me["wanted"] if w.lower().strip() in offered)
        if hits:
            out.append({"user_id": peer["id"], "hits": hits})
    out.sort(key=lambda r: (-r["hits"], str(r["user_id"])))
    return out[:n]
