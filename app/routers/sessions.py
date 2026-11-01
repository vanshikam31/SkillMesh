from fastapi import APIRouter, Depends, HTTPException
from skillmesh_ml import score_pair
from skillmesh_ml.scoring import shared_slots
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import current_user
from ..services import ml_profile, peer_out

router = APIRouter(prefix="/sessions", tags=["sessions"])


def to_out(s: models.Session, me: models.User, db: Session) -> schemas.SessionOut:
    req = s.request
    peer = req.receiver if req.sender_id == me.id else req.sender
    mine, theirs = ml_profile(me), ml_profile(peer)
    m = score_pair(mine, theirs)
    rating = db.scalar(select(models.Rating).where(models.Rating.session_id == s.id, models.Rating.rated_by == me.id))
    return schemas.SessionOut(id=s.id, peer=peer_out(peer), score=round(m["score"], 4), reasons=m["reasons"],
                              shared_slots=shared_slots(mine, theirs), slot=s.slot, completed=s.completed,
                              my_rating=rating.score if rating else None, feedback=rating.feedback if rating else "")


def get_my_session(session_id: int, me: models.User, db: Session) -> models.Session:
    s = db.get(models.Session, session_id)
    if not s or me.id not in (s.request.sender_id, s.request.receiver_id):
        raise HTTPException(404, "Session not found.")
    return s


@router.get("", response_model=list[schemas.SessionOut])
def list_sessions(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(models.Session).join(models.ConnectionRequest).where(
        or_(models.ConnectionRequest.sender_id == user.id, models.ConnectionRequest.receiver_id == user.id)
    ).order_by(models.Session.id.desc())).all()
    return [to_out(s, user, db) for s in rows]


@router.put("/{session_id}/schedule", response_model=schemas.SessionOut)
def schedule(session_id: int, data: schemas.ScheduleIn, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    s = get_my_session(session_id, user, db)
    s.slot = data.slot
    db.commit()
    return to_out(s, user, db)


@router.post("/{session_id}/complete", response_model=schemas.SessionOut)
def complete(session_id: int, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    s = get_my_session(session_id, user, db)
    s.completed = True
    db.commit()
    return to_out(s, user, db)


@router.post("/{session_id}/rating", response_model=schemas.SessionOut)
def rate_peer(session_id: int, data: schemas.RatingIn, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    s = get_my_session(session_id, user, db)
    if not s.completed:
        raise HTTPException(400, "Mark the session as done before rating.")
    if db.scalar(select(models.Rating).where(models.Rating.session_id == s.id, models.Rating.rated_by == user.id)):
        raise HTTPException(409, "You already rated this session.")
    peer = s.request.receiver if s.request.sender_id == user.id else s.request.sender
    db.add(models.Rating(session_id=s.id, rated_by=user.id, rated_user=peer.id, score=data.score, feedback=data.feedback.strip()))
    peer.rating_avg = (peer.rating_avg * peer.rating_count + data.score) / (peer.rating_count + 1)   # feeds future rankings
    peer.rating_count += 1
    db.commit()
    return to_out(s, user, db)
