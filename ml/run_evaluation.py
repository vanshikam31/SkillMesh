"""Run from the project root:  python ml/run_evaluation.py
Creates ml/data/synthetic_users.csv and prints Precision@K for the report."""
import os

from skillmesh_ml.evaluation import evaluate
from skillmesh_ml.synthetic_data import generate_users, write_csv

users = generate_users()
os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
write_csv(os.path.join(os.path.dirname(__file__), "data", "synthetic_users.csv"), users)
print("Dataset saved to ml/data/synthetic_users.csv")
for k in (3, 5, 8):
    r = evaluate(users, k)
    print(f"Precision@{k}: SkillMesh {r['skillmesh']:.0%} vs keyword {r['keyword']:.0%} ({r['students']} students)")
