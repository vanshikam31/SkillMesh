"""Step 2: skill similarity with TF-IDF (character n-grams) and cosine similarity."""
from functools import lru_cache

from sklearn.feature_extraction.text import TfidfVectorizer

from .preprocessing import normalize
from .synthetic_data import ALL_PHRASES

MATCH_THRESHOLD = 0.4  # below this, two skills are treated as unrelated

_vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 4), sublinear_tf=True)
_vectorizer.fit(sorted({normalize(p) for p in ALL_PHRASES}))


@lru_cache(maxsize=4096)
def _vec(phrase: str):
    return _vectorizer.transform([phrase])


def raw_cosine(a: str, b: str) -> float:
    return float((_vec(normalize(a)) @ _vec(normalize(b)).T).toarray()[0, 0])


def similarity(a: str, b: str) -> float:
    """0 when unrelated, 1 when identical after cleaning, otherwise the cosine score."""
    if normalize(a) == normalize(b):
        return 1.0
    c = raw_cosine(a, b)
    return c if c >= MATCH_THRESHOLD else 0.0


def coverage(wanted: list[str], offered: list[str]) -> float:
    """How well `offered` covers everything in `wanted` (0-1)."""
    if not wanted or not offered:
        return 0.0
    return sum(max(similarity(w, o) for o in offered) for w in wanted) / len(wanted)
