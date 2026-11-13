from fastapi import APIRouter, Depends, Query
from skillmesh_ml import get_top_matches
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .. import config, models, schemas
from ..database import get_db
from ..deps import current_user
from ..services import ml_profile, peer_out

router = APIRouter(tags=["recommendations"])


def request_status(db: Session, me_id: int, peer_id: int) -> str | None:
    req = db.scalar(select(models.ConnectionRequest).where(
        or_((models.ConnectionRequest.sender_id == me_id) & (models.ConnectionRequest.receiver_id == peer_id),
            (models.ConnectionRequest.sender_id == peer_id) & (models.ConnectionRequest.receiver_id == me_id))))
    if not req:
        return None
    if req.status == "pending":
        return "pending_out" if req.sender_id == me_id else "pending_in"
    return req.status


def candidate_users(db: Session, user: models.User) -> list[models.User]:
    """Real users, plus sample students depending on SAMPLE_USERS (on / off / auto)."""
    base = select(models.User).where(models.User.id != user.id, models.User.setup_done == True)  # noqa: E712
    real = list(db.scalars(base.where(models.User.is_sample == False)))  # noqa: E712
    if config.SAMPLE_USERS == "off":
        return real
    if config.SAMPLE_USERS == "auto" and len(real) >= config.SAMPLE_AUTO_THRESHOLD:
        return real
    return real + list(db.scalars(base.where(models.User.is_sample == True)))  # noqa: E712


@router.get("/recommendations", response_model=list[schemas.MatchOut])
def recommendations(n: int = Query(10, ge=1, le=50), user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    others = candidate_users(db, user)
    by_id = {u.id: u for u in others}
    top = get_top_matches(ml_profile(user), [ml_profile(u) for u in others], n)   # <- the AI/ML module
    return [schemas.MatchOut(peer=peer_out(by_id[m["user_id"]]), score=round(m["score"], 4), parts=m["parts"],
                             reasons=m["reasons"], request_status=request_status(db, user.id, m["user_id"])) for m in top]
