"""Chat between the two students of a session. The frontend polls GET every few seconds."""
from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .. import config, models, schemas
from ..database import get_db
from ..deps import current_user
from ..services import peer_out
from .sessions import get_my_session

router = APIRouter(prefix="/sessions", tags=["chat"])


def _out(m: models.Message, me_id: int) -> schemas.MessageOut:
    ts = m.created_at if m.created_at.tzinfo else m.created_at.replace(tzinfo=timezone.utc)
    return schemas.MessageOut(id=m.id, mine=m.sender_id == me_id, sender_name=m.sender.name, text=m.text,
                              created_at=ts.isoformat(), is_read=bool(m.is_read))


def _demo_reply(text: str) -> str:
    t = text.lower()
    if any(w in t for w in ("hi", "hello", "hey")):
        return "Hi! Happy to swap skills. When are you free?"
    if any(w in t for w in ("time", "slot", "when", "free", "available")):
        return "Any of our shared slots works for me. Pick one above and we are set."
    if "thank" in t:
        return "Anytime! See you in the session."
    return "Sounds good! Let us continue in our session."


def _my_sessions(db: Session, user: models.User) -> list[models.Session]:
    return list(db.scalars(select(models.Session).join(models.ConnectionRequest).where(
        models.ConnectionRequest.status == "accepted",
        or_(models.ConnectionRequest.sender_id == user.id, models.ConnectionRequest.receiver_id == user.id))))


def _unread(db: Session, session_id: int, user_id: int) -> int:
    return db.scalar(select(func.count(models.Message.id)).where(
        models.Message.session_id == session_id, models.Message.sender_id != user_id, models.Message.is_read == False)) or 0  # noqa: E712


@router.get("/conversations", response_model=list[schemas.ConversationOut])
def conversations(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    """All accepted connections with their latest message and unread count, most recent activity first."""
    rows = []
    for s in _my_sessions(db, user):
        peer = s.request.receiver if s.request.sender_id == user.id else s.request.sender
        last = db.scalar(select(models.Message).where(models.Message.session_id == s.id).order_by(models.Message.id.desc()).limit(1))
        ts = None
        if last:
            ts = (last.created_at if last.created_at.tzinfo else last.created_at.replace(tzinfo=timezone.utc)).isoformat()
        rows.append((ts or "", schemas.ConversationOut(session_id=s.id, peer=peer_out(peer), last_message=last.text if last else None, last_at=ts,
                                                      last_mine=(last.sender_id == user.id) if last else None, unread=_unread(db, s.id, user.id))))
    rows.sort(key=lambda r: (r[0], r[1].session_id), reverse=True)
    return [r[1] for r in rows]


@router.get("/unread")
def unread_total(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    return {"unread": sum(_unread(db, s.id, user.id) for s in _my_sessions(db, user))}


@router.post("/{session_id}/read")
def mark_read(session_id: int, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    """Marks the other student's messages in this conversation as read."""
    s = get_my_session(session_id, user, db)
    rows = db.scalars(select(models.Message).where(models.Message.session_id == s.id, models.Message.sender_id != user.id,
                                                   models.Message.is_read == False)).all()  # noqa: E712
    for m in rows:
        m.is_read = True
    db.commit()
    return {"marked": len(rows)}


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
