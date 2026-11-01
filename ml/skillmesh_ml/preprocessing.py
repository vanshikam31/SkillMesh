"""Step 1: clean skill text so that 'JS', 'js' and 'JavaScript' look the same to the model."""
import re

ALIASES = {
    "js": "javascript", "ml": "machine learning", "cpp": "c++", "py": "python",
    "dsa": "data structures algorithms", "reactjs": "react", "nodejs": "node",
}


def normalize(text: str) -> str:
    text = text.lower().replace(".", "")
    text = re.sub(r"[^a-z0-9+# ]+", " ", text)
    return " ".join(ALIASES.get(w, w) for w in text.split())


def normalize_range(value: float, low: float, high: float) -> float:
    """Scale a number (experience, rating) into the 0-1 range."""
    if high == low:
        return 0.0
    return max(0.0, min(1.0, (value - low) / (high - low)))
