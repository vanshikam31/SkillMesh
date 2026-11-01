from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db
from ..deps import current_user
from ..services import get_or_create_skills, profile_out

router = APIRouter(tags=["profile"])


@router.get("/profile", response_model=schemas.ProfileOut)
def get_profile(user: models.User = Depends(current_user)):
    return profile_out(user)


@router.put("/profile", response_model=schemas.ProfileOut)
def update_profile(data: schemas.ProfileIn, user: models.User = Depends(current_user), db: Session = Depends(get_db)):
    user.name, user.bio, user.experience = data.name.strip(), data.bio, data.experience
    user.availability = sorted(set(data.availability))
    user.offered = get_or_create_skills(db, data.offered)
    user.wanted = get_or_create_skills(db, data.wanted)
    user.setup_done = bool(user.offered and user.wanted)
    db.commit()
    return profile_out(user)


@router.get("/skills", response_model=list[str])
def skill_suggestions(db: Session = Depends(get_db)):
    return list(db.scalars(select(models.Skill.name).order_by(models.Skill.name)))
