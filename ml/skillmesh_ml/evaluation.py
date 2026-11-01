"""Step 5: Precision@K of SkillMesh vs exact keyword search, on synthetic data with hidden ground truth."""
from .matcher import get_top_matches, keyword_top


def is_relevant(a: dict, b: dict) -> bool:
    """A peer is truly relevant when the skill swap works in both directions."""
    return bool(set(a["wanted_ids"]) & set(b["offered_ids"])) and bool(set(b["wanted_ids"]) & set(a["offered_ids"]))


def evaluate(users: list[dict], k: int = 5, weights: dict | None = None) -> dict:
    mesh = kw = 0.0
    n = 0
    for me in users:
        relevant = {u["id"] for u in users if u["id"] != me["id"] and is_relevant(me, u)}
        if len(relevant) < k:
            continue
        n += 1
        mesh += sum(m["user_id"] in relevant for m in get_top_matches(me, users, k, weights)) / k
        kw += sum(m["user_id"] in relevant for m in keyword_top(me, users, k)) / k
    return {"k": k, "students": n, "skillmesh": mesh / n if n else 0.0, "keyword": kw / n if n else 0.0}
