"""Small schema updates for databases created by an older version (SQLite and PostgreSQL). Runs on every start, safe to repeat."""
from sqlalchemy import inspect, text

from . import models
from .database import SessionLocal, engine


def _columns(table: str) -> set[str]:
    return {c["name"] for c in inspect(engine).get_columns(table)}


def _add_boolean(table: str, column: str, default_true: bool = False) -> bool:
    """Adds a BOOLEAN column when it is missing. Returns True when it was added."""
    if column in _columns(table):
        return False
    sqlite = engine.dialect.name == "sqlite"
    default = ("1" if default_true else "0") if sqlite else ("TRUE" if default_true else "FALSE")
    with engine.begin() as conn:
        conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} BOOLEAN NOT NULL DEFAULT {default}"))
    return True


def ensure_schema() -> None:
    if _add_boolean("users", "is_sample"):
        db = SessionLocal()                  # the old seeded students are u01@example.com ... u48@example.com
        try:
            db.query(models.User).filter(models.User.email.like("u__@example.com")).update({"is_sample": True}, synchronize_session=False)
            db.commit()
        finally:
            db.close()
    if _add_boolean("messages", "is_read"):  # messages written before read-tracking existed count as read
        with engine.begin() as conn:
            conn.execute(text("UPDATE messages SET is_read = " + ("1" if engine.dialect.name == "sqlite" else "TRUE")))
