"""Glue between database objects and the ML module."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


def ml_profile(u: models.User) -> dict:
    """Convert a User row into the plain dict that skillmesh_ml expects."""
    return {"id": u.id, "offered": [s.name for s in u.offered], "wanted": [s.name for s in u.wanted],
            "experience": u.experience, "availability": list(u.availability or []), "rating": u.rating_avg}


def peer_out(u: models.User) -> schemas.PeerOut:
    return schemas.PeerOut(id=u.id, name=u.name, experience=u.experience, rating=round(u.rating_avg, 1),
                           rating_count=u.rating_count, offered=[s.name for s in u.offered], wanted=[s.name for s in u.wanted])


def profile_out(u: models.User) -> schemas.ProfileOut:
    return schemas.ProfileOut(id=u.id, email=u.email, name=u.name, bio=u.bio or "", experience=u.experience,
                              availability=list(u.availability or []), offered=[s.name for s in u.offered],
                              wanted=[s.name for s in u.wanted], setup_done=u.setup_done)


def get_or_create_skills(db: Session, names: list[str]) -> list[models.Skill]:
    skills, seen = [], set()
    for raw in names:
        name = " ".join(raw.lower().split())
        if not name or name in seen:
            continue
        seen.add(name)
        skill = db.scalar(select(models.Skill).where(models.Skill.name == name))
        if not skill:
            skill = models.Skill(name=name)
            db.add(skill)
        skills.append(skill)
    return skills
