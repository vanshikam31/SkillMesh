from fastapi import APIRouter, Depends, Query
from skillmesh_ml import get_top_matches
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .. import models, schemas
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


@router.get("/recommendations", response_model=list[schemas.MatchOut])
def recommendations(n: int = Query(10, ge=1, le=50), user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    others = db.scalars(select(models.User).where(models.User.id != user.id, models.User.setup_done == True)).all()  # noqa: E712
    by_id = {u.id: u for u in others}
    top = get_top_matches(ml_profile(user), [ml_profile(u) for u in others], n)   # <- the AI/ML module
    return [schemas.MatchOut(peer=peer_out(by_id[m["user_id"]]), score=round(m["score"], 4), parts=m["parts"],
                             reasons=m["reasons"], request_status=request_status(db, user.id, m["user_id"])) for m in top]
