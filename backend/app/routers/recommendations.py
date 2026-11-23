from fastapi import APIRouter, Depends, Query
from skillmesh_ml import category_of, get_top_matches, score_pair, similarity, skill_overlap
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


def _status_map(db: Session, me_id: int) -> dict[int, tuple[str, int | None]]:
    """peer id -> (request status as seen by me, session id)."""
    out = {}
    reqs = db.scalars(select(models.ConnectionRequest).where(
        or_(models.ConnectionRequest.sender_id == me_id, models.ConnectionRequest.receiver_id == me_id)))
    for r in reqs:
        peer_id = r.receiver_id if r.sender_id == me_id else r.sender_id
        status = ("pending_out" if r.sender_id == me_id else "pending_in") if r.status == "pending" else r.status
        out[peer_id] = (status, r.session.id if r.session else None)
    return out


def _discover(db: Session, user: models.User) -> list[tuple[models.User, dict, dict, dict]]:
    """Every candidate with its skill overlap and score, best score first."""
    me = ml_profile(user)
    rows = []
    for u in candidate_users(db, user):
        peer = ml_profile(u)
        rows.append((u, skill_overlap(me, peer), score_pair(me, peer)))
    rows.sort(key=lambda r: (-r[2]["score"], r[0].id))
    return rows


def _text_hit(skills: list[str], query: str) -> bool:
    q = query.lower().strip()
    return any(q in s.lower() or similarity(q, s) > 0 for s in skills)


def _match_out(db_status, u, overlap, scored) -> schemas.MatchOut:
    status, session_id = db_status.get(u.id, (None, None))
    return schemas.MatchOut(peer=peer_out(u), score=round(scored["score"], 4), parts=scored["parts"], reasons=scored["reasons"],
                            request_status=status, learn=overlap["learn"], teach=overlap["teach"],
                            mutual=bool(overlap["learn"] and overlap["teach"]), session_id=session_id)


@router.get("/recommendations/mutual", response_model=list[schemas.MatchOut])
def mutual_matches(n: int = Query(30, ge=1, le=100), user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    """Two-way matches: they offer what I want AND they want what I offer."""
    status = _status_map(db, user.id)
    return [_match_out(status, u, o, s) for u, o, s in _discover(db, user) if o["learn"] and o["teach"]][:n]


@router.get("/recommendations/explore", response_model=list[schemas.MatchOut])
def explore_other_skills(q: str = "", category: str = "", offered: str = "", wanted: str = "", n: int = Query(40, ge=1, le=100),
                         user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    """Everybody who is NOT a mutual match (so nobody appears twice), with optional filters."""
    status = _status_map(db, user.id)
    out = []
    for u, o, s in _discover(db, user):
        if o["learn"] and o["teach"]:
            continue                                            # already shown under Mutual Skill Matches
        offers, wants = [x.name for x in u.offered], [x.name for x in u.wanted]
        if q.strip() and q.strip().lower() not in u.name.lower():
            continue
        if category and not any(category_of(s_) == category for s_ in offers + wants):
            continue
        if offered.strip() and not _text_hit(offers, offered):
            continue
        if wanted.strip() and not _text_hit(wants, wanted):
            continue
        out.append(_match_out(status, u, o, s))
    return out[:n]
