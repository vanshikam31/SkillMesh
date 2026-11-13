"""Adds the is_sample column to databases created before it existed (SQLite and PostgreSQL)."""
from sqlalchemy import inspect, text

from . import models
from .database import SessionLocal, engine


def ensure_schema() -> None:
    if "is_sample" in {c["name"] for c in inspect(engine).get_columns("users")}:
        return
    default = "0" if engine.dialect.name == "sqlite" else "FALSE"
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE users ADD COLUMN is_sample BOOLEAN NOT NULL DEFAULT {default}"))
    db = SessionLocal()                      # the old seeded students are u01@example.com ... u48@example.com
    try:
        db.query(models.User).filter(models.User.email.like("u__@example.com")).update({"is_sample": True}, synchronize_session=False)
        db.commit()
    finally:
        db.close()
