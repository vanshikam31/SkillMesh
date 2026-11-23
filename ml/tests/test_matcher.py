from skillmesh_ml import get_top_matches, similarity
from skillmesh_ml.evaluation import evaluate
from skillmesh_ml.synthetic_data import generate_users


def test_similarity_handles_variants():
    assert similarity("python", "python programming") > 0.4
    assert similarity("js", "javascript") == 1.0
    assert similarity("python", "guitar") == 0.0


def test_top_matches_sorted_and_excludes_self():
    users = generate_users()
    res = get_top_matches(users[0], users, 5)
    assert len(res) == 5 and all(r["user_id"] != users[0]["id"] for r in res)
    assert res == sorted(res, key=lambda r: -r["score"])


def test_beats_keyword_baseline():
    r = evaluate(generate_users(), 5)
    assert r["skillmesh"] > r["keyword"]


def test_overlap_and_categories():
    from skillmesh_ml import category_of, skill_overlap
    me = {"id": 1, "offered": ["python"], "wanted": ["react"]}
    mutual = {"id": 2, "offered": ["reactjs"], "wanted": ["python programming"]}
    one_way = {"id": 3, "offered": ["react"], "wanted": ["guitar"]}
    none = {"id": 4, "offered": ["guitar"], "wanted": ["french"]}
    o = skill_overlap(me, mutual)
    assert o["learn"] == ["reactjs"] and o["teach"] == ["python programming"]
    o = skill_overlap(me, one_way)
    assert o["learn"] == ["react"] and o["teach"] == []
    assert skill_overlap(me, none) == {"learn": [], "teach": []}
    assert category_of("reactjs") == "Programming" and category_of("figma") == "Design and Media" and category_of("underwater basket weaving") == "Other"
