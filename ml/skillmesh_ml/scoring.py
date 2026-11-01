"""Step 3: compatibility score = weighted blend of five signals."""
from .preprocessing import normalize_range
from .similarity import coverage, similarity

DEFAULT_WEIGHTS = {"skill": 0.40, "reverse": 0.20, "exp": 0.15, "avail": 0.15, "rating": 0.10}


def shared_slots(a: dict, b: dict) -> list[str]:
    other = set(b.get("availability", []))
    return [s for s in a.get("availability", []) if s in other]


def score_pair(me: dict, peer: dict, weights: dict | None = None) -> dict:
    w = weights or DEFAULT_WEIGHTS
    parts = {
        "skill": coverage(me["wanted"], peer["offered"]),            # they can teach what I want
        "reverse": coverage(peer["wanted"], me["offered"]),          # I can teach what they want
        "exp": 1 - abs(me["experience"] - peer["experience"]) / 4,   # similar level
        "avail": min(1.0, len(shared_slots(me, peer)) / 3),          # 3+ shared slots = full score
        "rating": normalize_range(peer.get("rating", 0), 0, 5),
    }
    total = sum(w.get(k, 0) for k in parts)
    score = sum(w.get(k, 0) * v for k, v in parts.items()) / total if total else 0.0
    return {"score": score, "parts": parts, "reasons": explain(me, peer)}


def explain(me: dict, peer: dict) -> list[str]:
    teach = [max(peer["offered"], key=lambda o: similarity(w, o)) for w in me["wanted"]
             if any(similarity(w, o) for o in peer["offered"])]
    learn = [q for q in peer["wanted"] if any(similarity(q, o) for o in me["offered"])]
    out = []
    if teach:
        out.append("Can teach you " + ", ".join(dict.fromkeys(teach)))
    if learn:
        out.append("Wants to learn " + ", ".join(dict.fromkeys(learn)) + ", which you offer")
    n = len(shared_slots(me, peer))
    if n:
        out.append(f"{n} shared free {'slot' if n == 1 else 'slots'}")
    if not teach and not learn:
        out.insert(0, "Similar profile, no direct skill overlap yet")
    return out[:3]
