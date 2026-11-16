"""Chat between the two students of a session. The frontend polls GET every few seconds."""
from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import config, models, schemas
from ..database import get_db
from ..deps import current_user
from .sessions import get_my_session

router = APIRouter(prefix="/sessions", tags=["chat"])


def _out(m: models.Message, me_id: int) -> schemas.MessageOut:
    ts = m.created_at if m.created_at.tzinfo else m.created_at.replace(tzinfo=timezone.utc)
    return schemas.MessageOut(id=m.id, mine=m.sender_id == me_id, text=m.text, created_at=ts.isoformat())


def _demo_reply(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ("hi", "hello", "hey")):
        return "Hi! Happy to swap skills. When are you free?"
    if any(w in t for w in ("time", "slot", "when", "free", "available")):
        return "Any of our shared slots works for me. Pick one above and we are set."
    if "thank" in t:
        return "Anytime! See you in the session."
    return "Sounds good! Let us continue in our session."


@router.get("/{session_id}/messages", response_model=list[schemas.MessageOut])
def list_messages(session_id: int, after: int = 0, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    s = get_my_session(session_id, user, db)
    rows = db.scalars(select(models.Message).where(models.Message.session_id == s.id, models.Message.id > after).order_by(models.Message.id)).all()
    return [_out(m, user.id) for m in rows]


@router.post("/{session_id}/messages", response_model=schemas.MessageOut, status_code=201)
def send_message(session_id: int, data: schemas.MessageIn, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    s = get_my_session(session_id, user, db)
    text = data.text.strip()
    if not text:
        raise HTTPException(400, "Write a message first.")
    msg = models.Message(session_id=s.id, sender_id=user.id, text=text)
    db.add(msg)
    db.flush()
    peer = s.request.receiver if s.request.sender_id == user.id else s.request.sender
    if peer.is_sample and config.SAMPLE_AUTO_REPLY:          # demo students answer by themselves
        db.add(models.Message(session_id=s.id, sender_id=peer.id, text=_demo_reply(text)))
    db.commit()
    return _out(msg, user.id)
