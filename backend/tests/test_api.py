import os
import tempfile

os.environ["DATABASE_URL"] = "sqlite:///" + os.path.join(tempfile.mkdtemp(), "test.db")

from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

client = TestClient(app)


def signup(name, email):
    r = client.post("/auth/register", json={"name": name, "email": email, "password": "secret1"})
    assert r.status_code == 201
    return {"Authorization": "Bearer " + r.json()["token"]}


def setup(h, offered, wanted, slots):
    r = client.put("/profile", headers=h, json={"name": "x", "experience": 2, "offered": offered, "wanted": wanted, "availability": slots})
    assert r.status_code == 200 and r.json()["setup_done"]


def test_full_flow():
    a = signup("Asha", "asha@example.com")
    b = signup("Ben", "ben@example.com")
    setup(a, ["python"], ["react"], ["Mon-E", "Wed-E", "Sat-A"])
    setup(b, ["reactjs"], ["python programming"], ["Mon-E", "Wed-E", "Sat-A"])
    assert client.post("/auth/register", json={"name": "A", "email": "asha@example.com", "password": "secret1"}).status_code == 409
    assert client.post("/auth/login", json={"email": "asha@example.com", "password": "bad-pass"}).status_code == 401

    recs = client.get("/recommendations", headers=a).json()
    assert len(recs) == 1 and recs[0]["score"] > 0.6 and recs[0]["reasons"]

    req = client.post("/requests", headers=a, json={"receiver_id": recs[0]["peer"]["id"]}).json()
    assert client.post(f"/requests/{req['id']}/respond", headers=b, json={"action": "accept"}).json()["status"] == "accepted"

    s = client.get("/sessions", headers=a).json()[0]
    assert s["shared_slots"]
    assert client.put(f"/sessions/{s['id']}/schedule", headers=a, json={"slot": s["shared_slots"][0]}).json()["slot"]
    assert client.post(f"/sessions/{s['id']}/rating", headers=a, json={"score": 5}).status_code == 400   # not completed yet
    client.post(f"/sessions/{s['id']}/complete", headers=a)
    done = client.post(f"/sessions/{s['id']}/rating", headers=a, json={"score": 5, "feedback": "Great teacher"}).json()
    assert done["my_rating"] == 5 and done["peer"]["rating_count"] == 1


def test_auth_required_and_matching_endpoints():
    assert client.get("/recommendations").status_code == 401
    assert client.get("/matching/evaluation?k=3").json()["skillmesh"] > 0
    assert client.get("/matching/similarity?a=js&b=javascript").json()["is_match"]


def test_forgot_and_reset_password():
    h = signup("Riya", "riya@example.com")
    # unknown email gets the same generic answer and no link
    unknown = client.post("/auth/forgot-password", json={"email": "nobody@example.com"}).json()
    assert "dev_reset_link" not in unknown and unknown["message"]

    link = client.post("/auth/forgot-password", json={"email": "riya@example.com"}).json()["dev_reset_link"]
    token = link.split("token=")[1]
    # a reset token must not work as a login token
    assert client.get("/auth/me", headers={"Authorization": "Bearer " + token}).status_code == 401

    assert client.post("/auth/reset-password", json={"token": token, "new_password": "newsecret"}).status_code == 200
    assert client.post("/auth/login", json={"email": "riya@example.com", "password": "secret1"}).status_code == 401
    assert client.post("/auth/login", json={"email": "riya@example.com", "password": "newsecret"}).status_code == 200
    # the link works only once
    assert client.post("/auth/reset-password", json={"token": token, "new_password": "another1"}).status_code == 400
    assert client.post("/auth/reset-password", json={"token": "garbage", "new_password": "another1"}).status_code == 400


def test_sample_user_switch():
    from app import config, models
    from app.database import SessionLocal
    from app.services import get_or_create_skills

    db = SessionLocal()
    db.add(models.User(name="Sam Sample", email="u99@example.com", password_hash="x", experience=2, availability=["Mon-E"],
                       setup_done=True, is_sample=True, offered=get_or_create_skills(db, ["react"]), wanted=get_or_create_skills(db, ["python"])))
    db.commit()
    db.close()
    h = signup("Real One", "real1@example.com")
    setup(h, ["python"], ["react"], ["Mon-E"])
    old = (config.SAMPLE_USERS, config.SAMPLE_AUTO_THRESHOLD)
    try:
        def samples_shown():
            return any(m["peer"]["is_sample"] for m in client.get("/recommendations?n=50", headers=h).json())
        config.SAMPLE_USERS = "on"
        assert samples_shown()
        config.SAMPLE_USERS = "off"
        assert not samples_shown()
        config.SAMPLE_USERS, config.SAMPLE_AUTO_THRESHOLD = "auto", 100      # few real users: samples fill the list
        assert samples_shown()
        config.SAMPLE_AUTO_THRESHOLD = 1                                      # enough real users: samples disappear
        assert not samples_shown()
    finally:
        config.SAMPLE_USERS, config.SAMPLE_AUTO_THRESHOLD = old


def test_chat_and_sample_auto_reply():
    from app import models
    from app.database import SessionLocal
    from app.services import get_or_create_skills

    a, b = signup("Chat A", "chata@example.com"), signup("Chat B", "chatb@example.com")
    setup(a, ["python"], ["react"], ["Mon-E"])
    setup(b, ["react"], ["python"], ["Mon-E"])
    bid = client.get("/auth/me", headers=b).json()["id"]
    req = client.post("/requests", headers=a, json={"receiver_id": bid}).json()
    assert req["status"] == "pending"
    client.post(f"/requests/{req['id']}/respond", headers=b, json={"action": "accept"})
    sid = client.get("/sessions", headers=a).json()[0]["id"]

    assert client.post(f"/sessions/{sid}/messages", headers=a, json={"text": "  Hi!  "}).json()["text"] == "Hi!"
    client.post(f"/sessions/{sid}/messages", headers=b, json={"text": "Hello"})
    msgs = client.get(f"/sessions/{sid}/messages", headers=a).json()
    assert [m["mine"] for m in msgs] == [True, False]
    assert client.get(f"/sessions/{sid}/messages?after={msgs[0]['id']}", headers=a).json()[0]["text"] == "Hello"
    outsider = signup("Outsider", "outsider@example.com")
    assert client.get(f"/sessions/{sid}/messages", headers=outsider).status_code == 404
    assert client.post(f"/sessions/{sid}/messages", headers=a, json={"text": "   "}).status_code == 400

    db = SessionLocal()
    db.add(models.User(name="Demo Dee", email="u97@example.com", password_hash="x", experience=2, availability=["Mon-E"], setup_done=True,
                       is_sample=True, offered=get_or_create_skills(db, ["react"]), wanted=get_or_create_skills(db, ["python"])))
    db.commit()
    sample_id = db.query(models.User).filter_by(email="u97@example.com").one().id
    db.close()
    assert client.post("/requests", headers=a, json={"receiver_id": sample_id}).json()["status"] == "accepted"
    sess = [s for s in client.get("/sessions", headers=a).json() if s["peer"]["id"] == sample_id][0]
    client.post(f"/sessions/{sess['id']}/messages", headers=a, json={"text": "Hi Dee, when are you free?"})
    msgs = client.get(f"/sessions/{sess['id']}/messages", headers=a).json()
    assert len(msgs) == 2 and msgs[1]["mine"] is False
