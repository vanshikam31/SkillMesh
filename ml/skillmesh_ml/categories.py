"""Skill categories, used by the Explore Other Skills filters."""
from functools import lru_cache

from .similarity import similarity
from .synthetic_data import CANON

CATEGORY_OF_CANON = {
    "python": "Programming", "javascript": "Programming", "react": "Programming", "c++": "Programming", "java": "Programming",
    "dsa": "Programming", "git": "Programming", "fastapi": "Programming",
    "sql": "Data and AI", "machine learning": "Data and AI", "data analysis": "Data and AI",
    "ui design": "Design and Media", "photoshop": "Design and Media", "video editing": "Design and Media",
    "guitar": "Music", "public speaking": "Communication", "content writing": "Communication",
    "french": "Languages", "digital marketing": "Business", "arduino": "Electronics",
}
CATEGORIES = sorted(set(CATEGORY_OF_CANON.values())) + ["Other"]


@lru_cache(maxsize=2048)
def category_of(skill: str) -> str:
    """Category of the most similar known skill, or 'Other' when nothing is similar enough."""
    best, best_score = "Other", 0.0
    for canon, variants in CANON.items():
        score = max(similarity(skill, v) for v in variants)
        if score > best_score:
            best, best_score = CATEGORY_OF_CANON[canon], score
    return best
