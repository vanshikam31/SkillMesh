# AI/ML engine (Vanshika)

Python package `skillmesh_ml`. It has no web code. The backend just calls `get_top_matches(me, candidates, n)`.

| File | What it does | Report section |
|---|---|---|
| `preprocessing.py` | lowercase, clean text, expand abbreviations (js -> javascript), 0-1 scaling | Preprocessing |
| `synthetic_data.py` | 48 synthetic students with hidden ground truth, CSV export | Dataset |
| `similarity.py` | TF-IDF (character 3-4 grams) + cosine similarity, threshold 0.4 | Skill similarity |
| `scoring.py` | compatibility score and the "why this match" reasons | Scoring |
| `matcher.py` | ranks peers, plus the exact-keyword baseline | Ranking |
| `evaluation.py` | Precision@K, SkillMesh vs keyword search | Evaluation |

Score = 0.40 x skill_match + 0.20 x reverse_match + 0.15 x experience + 0.15 x availability + 0.10 x rating

Run (from the project root, venv active):
```
python ml/run_evaluation.py     # prints Precision@K, writes ml/data/synthetic_users.csv
pytest ml                       # unit tests
```
Upgrade ideas: Sentence-BERT embeddings in `similarity.py` (same function names, so nothing else changes); learn the weights from real session ratings.
