import logging

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..config import FRONTEND_URL, SHOW_RESET_LINK
from ..database import get_db
from ..deps import current_user
from ..emailer import send_reset_email, smtp_configured
from ..security import (create_reset_token, create_token, hash_password, password_fingerprint, read_reset_token,
                        verify_password)
from ..services import profile_out

router = APIRouter(prefix="/auth", tags=["auth"])
log = logging.getLogger("uvicorn.error")


@router.post("/register", response_model=schemas.TokenOut, status_code=201)
def register(data: schemas.RegisterIn, db: Session = Depends(get_db)):
    email = data.email.lower()
    if db.scalar(select(models.User).where(models.User.email == email)):
        raise HTTPException(409, "This email is already registered. Please sign in instead.")
    user = models.User(name=data.name.strip(), email=email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    return {"token": create_token(user.id), "user": profile_out(user)}


@router.post("/login", response_model=schemas.TokenOut)
def login(data: schemas.LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(models.User).where(models.User.email == data.email.lower()))
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "Email or password is incorrect.")
    return {"token": create_token(user.id), "user": profile_out(user)}


@router.get("/me", response_model=schemas.ProfileOut)
def me(user: models.User = Depends(current_user)):
    return profile_out(user)


@router.post("/forgot-password")
def forgot_password(data: schemas.ForgotIn, background: BackgroundTasks, db: Session = Depends(get_db)):
    """Always answers the same way, so nobody can use this form to find out which emails are registered."""
    result = {"message": "If an account exists for this email, a reset link has been sent. Check your inbox."}
    user = db.scalar(select(models.User).where(models.User.email == data.email.lower()))
    if user:
        link = f"{FRONTEND_URL}/reset-password?token={create_reset_token(user.id, user.password_hash)}"
        if smtp_configured():
            background.add_task(send_reset_email, user.email, link)
        else:
            log.warning("SMTP is not set up. Password reset link for %s: %s", user.email, link)
            if SHOW_RESET_LINK:
                result["dev_reset_link"] = link
    return result


@router.post("/reset-password")
def reset_password(data: schemas.ResetIn, db: Session = Depends(get_db)):
    parsed = read_reset_token(data.token)
    user = db.get(models.User, parsed[0]) if parsed else None
    if not user or password_fingerprint(user.password_hash) != parsed[1]:
        raise HTTPException(400, "This reset link is invalid or has expired. Please request a new one.")
    user.password_hash = hash_password(data.new_password)
    db.commit()
    return {"message": "Password updated. You can sign in now."}
