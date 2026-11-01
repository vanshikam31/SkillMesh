"""Fill the database with 48 synthetic students so recommendations have people to show.
Run from the project root:  python backend/seed.py      (all seeded accounts use the password: password123)"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from skillmesh_ml.synthetic_data import generate_users  # noqa: E402

from app import models  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.security import hash_password  # noqa: E402
from app.services import get_or_create_skills  # noqa: E402

Base.metadata.create_all(bind=engine)
db = SessionLocal()
pw = hash_password("password123")
created = 0
for u in generate_users():
    email = f"{u['id']}@example.com"
    if db.query(models.User).filter_by(email=email).first():
        continue
    db.add(models.User(name=u["name"], email=email, password_hash=pw, experience=u["experience"], availability=u["availability"],
                       setup_done=True, rating_avg=u["rating"], rating_count=u["rating_count"],
                       offered=get_or_create_skills(db, u["offered"]), wanted=get_or_create_skills(db, u["wanted"])))
    db.flush()
    created += 1
db.commit()
print(f"Seeded {created} students. Log in with u01@example.com / password123 to test.")
