"""See real users and manage the sample students.   Run from the project root (venv active):

    python backend/manage_users.py stats             how many real and sample users exist
    python backend/manage_users.py list              list the real users (name, email, skills)
    python backend/manage_users.py remove-samples    delete all sample students (asks first; add --yes to skip asking)

Works on whichever database DATABASE_URL points to (local SQLite by default, Neon when you set it)."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import or_  # noqa: E402

from app import models  # noqa: E402
from app.database import Base, SessionLocal, engine  # noqa: E402
from app.migrate import ensure_schema  # noqa: E402

Base.metadata.create_all(bind=engine)
ensure_schema()
db = SessionLocal()
cmd = sys.argv[1] if len(sys.argv) > 1 else "stats"
real = db.query(models.User).filter(models.User.is_sample == False).order_by(models.User.id).all()  # noqa: E712
samples = db.query(models.User).filter(models.User.is_sample == True).all()  # noqa: E712

if cmd == "stats":
    print(f"Real users:   {len(real)} ({sum(u.setup_done for u in real)} finished their profile)")
    print(f"Sample users: {len(samples)}")
elif cmd == "list":
    if not real:
        print("No real users yet.")
    for u in real:
        print(f"#{u.id:<4} {u.name:<22} {u.email:<32} profile {'done' if u.setup_done else 'pending':<8} "
              f"teaches: {', '.join(s.name for s in u.offered) or '-'} | wants: {', '.join(s.name for s in u.wanted) or '-'}")
elif cmd == "remove-samples":
    if not samples:
        print("There are no sample users.")
    elif "--yes" in sys.argv or input(f"Delete {len(samples)} sample students and their requests? Type yes: ").strip().lower() == "yes":
        ids = [u.id for u in samples]
        req_ids = [r.id for r in db.query(models.ConnectionRequest).filter(or_(models.ConnectionRequest.sender_id.in_(ids), models.ConnectionRequest.receiver_id.in_(ids)))]
        ses_ids = [s.id for s in db.query(models.Session).filter(models.Session.request_id.in_(req_ids))] if req_ids else []
        db.query(models.Rating).filter(or_(models.Rating.rated_by.in_(ids), models.Rating.rated_user.in_(ids),
                                           models.Rating.session_id.in_(ses_ids or [-1]))).delete(synchronize_session=False)
        if ses_ids:
            db.query(models.Session).filter(models.Session.id.in_(ses_ids)).delete(synchronize_session=False)
        if req_ids:
            db.query(models.ConnectionRequest).filter(models.ConnectionRequest.id.in_(req_ids)).delete(synchronize_session=False)
        for u in samples:
            db.delete(u)
        db.commit()
        print(f"Deleted {len(ids)} sample students.")
    else:
        print("Cancelled.")
else:
    print(__doc__)
