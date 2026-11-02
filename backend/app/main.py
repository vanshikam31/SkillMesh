from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models  # noqa: F401  (registers the tables)
from .config import CORS_ORIGINS
from .database import Base, engine
from .routers import auth, matching, profile, recommendations, requests, sessions

Base.metadata.create_all(bind=engine)

app = FastAPI(title="SkillMesh API", version="1.0.0",
              description="Peer skill matching platform. Interactive docs are at /docs.")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
for r in (auth, profile, recommendations, requests, sessions, matching):
    app.include_router(r.router)


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return {
        "message": "Welcome to SkillMesh API",
        "status": "running",
        "docs": "/docs"
    }