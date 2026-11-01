# Backend and database (Divya)

FastAPI + SQLAlchemy. SQLite by default (no setup), PostgreSQL when `DATABASE_URL` is set.

| File | Purpose |
|---|---|
| `app/main.py` | creates the app, CORS, registers routers |
| `app/models.py` | tables: users, skills, user_skills_offered, user_skills_wanted, connection_requests, sessions, ratings |
| `app/schemas.py` | Pydantic request/response shapes |
| `app/security.py`, `app/deps.py` | bcrypt password hashing, JWT tokens, "current user" dependency |
| `app/services.py` | converts database rows to the dicts the ML module needs |
| `app/routers/` | auth, profile, recommendations (calls the ML module), requests, sessions (+ ratings), matching |
| `seed.py` | adds 48 sample students (password `password123`) |
| `tests/test_api.py` | full flow test: register, profile, recommend, request, accept, schedule, rate |

Run (from the project root, venv active):
```
python backend/seed.py
cd backend
uvicorn app.main:app --reload --port 8000     # API docs: http://localhost:8000/docs
pytest
```

Main endpoints: `POST /auth/register`, `POST /auth/login`, `GET/PUT /profile`, `GET /recommendations`,
`POST /requests`, `POST /requests/{id}/respond`, `GET /sessions`, `PUT /sessions/{id}/schedule`,
`POST /sessions/{id}/complete`, `POST /sessions/{id}/rating`, `GET /matching/evaluation`.
