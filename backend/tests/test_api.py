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


def test_reset_email_is_sent_when_smtp_is_configured(monkeypatch):
    from app import config, emailer

    sent = []

    class FakeSMTP:
        def __init__(self, host, port, timeout=None): sent.append(("connect", host, port))
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def ehlo(self): pass
        def starttls(self, context=None): sent.append(("starttls",))
        def login(self, user, pw): sent.append(("login", user))
        def send_message(self, msg): sent.append(("message", msg["To"], msg.get_content()))

    monkeypatch.setattr(emailer.smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(config, "SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr(config, "SMTP_USER", "me@example.com")
    monkeypatch.setattr(config, "SMTP_PASSWORD", "app-password")
    signup("Mailer", "mailer@example.com")
    body = client.post("/auth/forgot-password", json={"email": "mailer@example.com"}).json()
    assert "dev_reset_link" not in body                     # with SMTP set, the link goes to the inbox only
    message = [s for s in sent if s[0] == "message"][0]
    assert message[1] == "mailer@example.com" and "/reset-password?token=" in message[2]
    assert ("starttls",) in sent and ("login", "me@example.com") in sent


def _uid(h):
    return client.get("/auth/me", headers=h).json()["id"]


def _profile(h, name, offered, wanted, slots=("Mon-E",)):
    r = client.put("/profile", headers=h, json={"name": name, "experience": 2, "offered": offered, "wanted": wanted, "availability": list(slots)})
    assert r.status_code == 200


def test_mutual_and_explore_sections():
    me = signup("Disc Me", "discme@example.com")
    m = signup("Mutual Mia", "mia@example.com")
    o1 = signup("Oneway Omar", "omar@example.com")
    o2 = signup("Other Olga", "olga@example.com")
    _profile(me, "Disc Me", ["python"], ["react"])
    _profile(m, "Mutual Mia", ["reactjs"], ["python programming"])      # offers what I want AND wants what I offer
    _profile(o1, "Oneway Omar", ["react"], ["guitar"])                   # offers what I want, wants something else
    _profile(o2, "Other Olga", ["guitar"], ["french"])                   # no overlap at all
    ids = {"m": _uid(m), "o1": _uid(o1), "o2": _uid(o2), "me": _uid(me)}

    mutual = client.get("/recommendations/mutual", headers=me).json()
    explore = client.get("/recommendations/explore", headers=me).json()
    mutual_ids, explore_ids = {x["peer"]["id"] for x in mutual}, {x["peer"]["id"] for x in explore}
    assert ids["m"] in mutual_ids and ids["m"] not in explore_ids
    assert {ids["o1"], ids["o2"]} <= explore_ids and not ({ids["o1"], ids["o2"]} & mutual_ids)
    assert not (mutual_ids & explore_ids) and ids["me"] not in mutual_ids | explore_ids      # nobody twice, never myself
    mia = [x for x in mutual if x["peer"]["id"] == ids["m"]][0]
    assert mia["mutual"] and mia["learn"] == ["reactjs"] and mia["teach"] == ["python programming"]
    omar = [x for x in explore if x["peer"]["id"] == ids["o1"]][0]
    assert not omar["mutual"] and omar["learn"] == ["react"] and omar["teach"] == []
    assert omar["peer"]["offered"] == ["react"] and omar["peer"]["wanted"] == ["guitar"]

    def explore_ids_for(**params):
        return {x["peer"]["id"] for x in client.get("/recommendations/explore", headers=me, params=params).json()}
    assert explore_ids_for(q="olga") == {ids["o2"]}                                   # search by username
    assert ids["o2"] in explore_ids_for(category="Music") and ids["o1"] in explore_ids_for(category="Music")
    assert explore_ids_for(offered="guitar") >= {ids["o2"]} and ids["o1"] not in explore_ids_for(offered="guitar")
    assert ids["o2"] in explore_ids_for(wanted="french") and ids["o1"] not in explore_ids_for(wanted="french")
    assert "Music" in client.get("/skills/categories").json()


def test_requests_rules_and_chat_inbox():
    a, b = signup("Inbox A", "inboxa@example.com"), signup("Inbox B", "inboxb@example.com")
    _profile(a, "Inbox A", ["python"], ["react"])
    _profile(b, "Inbox B", ["react"], ["python"])
    aid, bid = _uid(a), _uid(b)
    assert client.post("/requests", headers=a, json={"receiver_id": aid}).status_code == 400          # not to myself
    req = client.post("/requests", headers=a, json={"receiver_id": bid}).json()
    assert client.post("/requests", headers=a, json={"receiver_id": bid}).status_code == 409          # no duplicates
    assert client.post("/requests", headers=b, json={"receiver_id": aid}).status_code == 409          # ...in either direction
    assert client.post(f"/requests/{req['id']}/respond", headers=a, json={"action": "accept"}).status_code == 404   # sender cannot accept

    # nothing to chat about before the request is accepted
    assert client.get("/sessions/conversations", headers=a).json() == []
    assert client.post(f"/requests/{req['id']}/respond", headers=b, json={"action": "accept"}).json()["session_id"]

    sid = client.get("/sessions", headers=a).json()[0]["id"]
    for text in ("Hi B!", "Are you free on Monday?"):
        client.post(f"/sessions/{sid}/messages", headers=a, json={"text": text})
    inbox_b = client.get("/sessions/conversations", headers=b).json()
    assert len(inbox_b) == 1 and inbox_b[0]["unread"] == 2 and inbox_b[0]["last_message"] == "Are you free on Monday?" and inbox_b[0]["last_mine"] is False
    assert client.get("/sessions/conversations", headers=a).json()[0]["unread"] == 0                  # my own messages are not unread
    assert client.get("/sessions/unread", headers=b).json()["unread"] == 2
    msgs = client.get(f"/sessions/{sid}/messages", headers=b).json()
    assert msgs[0]["sender_name"] == "Inbox A" and msgs[0]["is_read"] is False

    outsider = signup("Inbox C", "inboxc@example.com")
    assert client.post(f"/sessions/{sid}/read", headers=outsider).status_code == 404                  # cannot touch other people's chats
    assert client.get(f"/sessions/{sid}/messages", headers=outsider).status_code == 404
    assert client.post(f"/sessions/{sid}/messages", headers=outsider, json={"text": "hi"}).status_code == 404

    assert client.post(f"/sessions/{sid}/read", headers=b).json()["marked"] == 2
    assert client.get("/sessions/unread", headers=b).json()["unread"] == 0
    client.post(f"/sessions/{sid}/messages", headers=b, json={"text": "Yes, Monday works"})
    assert client.get("/sessions/conversations", headers=a).json()[0]["unread"] == 1
    # messages survive logout and login: they live in the database
    again = client.post("/auth/login", json={"email": "inboxa@example.com", "password": "secret1"}).json()["token"]
    assert len(client.get(f"/sessions/{sid}/messages", headers={"Authorization": "Bearer " + again}).json()) == 3


def test_reject_request():
    a, b = signup("Rej A", "reja@example.com"), signup("Rej B", "rejb@example.com")
    _profile(a, "Rej A", ["python"], ["react"])
    _profile(b, "Rej B", ["react"], ["python"])
    req = client.post("/requests", headers=a, json={"receiver_id": _uid(b)}).json()
    assert client.post(f"/requests/{req['id']}/respond", headers=b, json={"action": "reject"}).json()["status"] == "declined"
    assert client.get("/sessions/conversations", headers=a).json() == []                              # rejected: no chat
