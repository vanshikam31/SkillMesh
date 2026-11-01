from fastapi import APIRouter, Depends, HTTPException
from skillmesh_ml import score_pair
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import current_user
from ..services import ml_profile, peer_out

router = APIRouter(prefix="/requests", tags=["requests"])


def to_out(req: models.ConnectionRequest, me: models.User) -> schemas.RequestOut:
    peer = req.receiver if req.sender_id == me.id else req.sender
    m = score_pair(ml_profile(me), ml_profile(peer))
    return schemas.RequestOut(id=req.id, direction="out" if req.sender_id == me.id else "in", status=req.status,
                              peer=peer_out(peer), score=round(m["score"], 4), reasons=m["reasons"])


@router.get("", response_model=list[schemas.RequestOut])
def list_requests(user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    reqs = db.scalars(select(models.ConnectionRequest).where(
        or_(models.ConnectionRequest.sender_id == user.id, models.ConnectionRequest.receiver_id == user.id)
    ).order_by(models.ConnectionRequest.id.desc())).all()
    return [to_out(r, user) for r in reqs]


@router.post("", response_model=schemas.RequestOut, status_code=201)
def send_request(data: schemas.RequestIn, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    peer = db.get(models.User, data.receiver_id)
    if not peer or peer.id == user.id:
        raise HTTPException(400, "Choose another student.")
    exists = db.scalar(select(models.ConnectionRequest).where(
        or_((models.ConnectionRequest.sender_id == user.id) & (models.ConnectionRequest.receiver_id == peer.id),
            (models.ConnectionRequest.sender_id == peer.id) & (models.ConnectionRequest.receiver_id == user.id))))
    if exists:
        raise HTTPException(409, "A request with this student already exists.")
    req = models.ConnectionRequest(sender_id=user.id, receiver_id=peer.id)
    db.add(req)
    db.commit()
    return to_out(req, user)


@router.post("/{request_id}/respond", response_model=schemas.RequestOut)
def respond(request_id: int, data: schemas.RespondIn, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    req = db.get(models.ConnectionRequest, request_id)
    if not req or req.receiver_id != user.id:
        raise HTTPException(404, "Request not found.")
    if req.status != "pending":
        raise HTTPException(409, "This request was already answered.")
    req.status = "accepted" if data.action == "accept" else "declined"
    if req.status == "accepted":
        db.add(models.Session(request=req))      # a session is created as soon as a request is accepted
    db.commit()
    return to_out(req, user)
