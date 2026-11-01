from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from . import models
from .database import get_db
from .security import decode_token

bearer = HTTPBearer(auto_error=False)


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)) -> models.User:
    user_id = decode_token(creds.credentials) if creds else None
    user = db.get(models.User, user_id) if user_id else None
    if not user:
        raise HTTPException(401, "Please sign in again.")
    return user
