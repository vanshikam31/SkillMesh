"""Powers the 'How matching works' page: evaluation against keyword search and a similarity tester."""
from functools import lru_cache

from fastapi import APIRouter, Query
from skillmesh_ml import DEFAULT_WEIGHTS
from skillmesh_ml.evaluation import evaluate
from skillmesh_ml.preprocessing import normalize
from skillmesh_ml.similarity import MATCH_THRESHOLD, raw_cosine, similarity
from skillmesh_ml.synthetic_data import generate_users

router = APIRouter(prefix="/matching", tags=["matching"])
_USERS = generate_users()


@lru_cache(maxsize=256)
def _cached_eval(k: int, skill: float, reverse: float, exp: float, avail: float, rating: float) -> dict:
    return evaluate(_USERS, k, {"skill": skill, "reverse": reverse, "exp": exp, "avail": avail, "rating": rating})


@router.get("/evaluation")
def evaluation(k: int = Query(5, ge=1, le=10), skill: float = DEFAULT_WEIGHTS["skill"], reverse: float = DEFAULT_WEIGHTS["reverse"],
               exp: float = DEFAULT_WEIGHTS["exp"], avail: float = DEFAULT_WEIGHTS["avail"], rating: float = DEFAULT_WEIGHTS["rating"]):
    return _cached_eval(k, round(skill, 2), round(reverse, 2), round(exp, 2), round(avail, 2), round(rating, 2))


@router.get("/similarity")
def skill_similarity(a: str = "python", b: str = "python programming"):
    return {"score": round(1.0 if normalize(a) == normalize(b) else raw_cosine(a, b), 3),
            "is_match": similarity(a, b) > 0, "threshold": MATCH_THRESHOLD}
