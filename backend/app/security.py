from datetime import datetime, timedelta, timezone

import hashlib

import bcrypt
import jwt

from .config import ACCESS_TOKEN_EXPIRE_MINUTES, RESET_TOKEN_MINUTES, SECRET_KEY


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def create_token(user_id: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": str(user_id), "exp": exp}, SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> int | None:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if payload.get("purpose"):          # reset-password tokens must never work as login tokens
            return None
        return int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        return None


def password_fingerprint(password_hash: str) -> str:
    """Changes whenever the password changes, so a reset link works only once."""
    return hashlib.sha256(password_hash.encode()).hexdigest()[:16]


def create_reset_token(user_id: int, password_hash: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=RESET_TOKEN_MINUTES)
    return jwt.encode({"sub": str(user_id), "purpose": "reset", "fp": password_fingerprint(password_hash), "exp": exp},
                      SECRET_KEY, algorithm="HS256")


def read_reset_token(token: str) -> tuple[int, str] | None:
    try:
        p = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if p.get("purpose") != "reset":
            return None
        return int(p["sub"]), p["fp"]
    except (jwt.PyJWTError, KeyError, ValueError):
        return None
