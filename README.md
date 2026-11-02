# SkillMesh: AI-powered peer skill matching and learning platform

Students list skills they can teach and skills they want to learn. SkillMesh ranks the best learning partners
with TF-IDF similarity and a weighted compatibility score, then supports requests, sessions and feedback.

```
skillmesh/
├── frontend/   React UI                       (Ruchika)   see frontend/README.md
├── backend/    FastAPI + PostgreSQL           (Divya)     see backend/README.md
├── ml/         AI/ML matching engine          (Vanshika)  see ml/README.md
├── requirements.txt   installs ml + backend into ONE virtual environment
├── render.yaml        backend + database deployment (Render)
└── .vscode/           interpreter, tasks, recommended extensions
```
How the parts connect: **React** calls the **FastAPI** REST API. The API stores data in the database and calls
`get_top_matches()` from the **ml** package for `/recommendations`.

## 1. Install once

You need Python 3.10+, Node.js 18+ and Git. Open the `skillmesh` folder in VS Code (File > Open Folder), then open a terminal (Ctrl+`).

**Create and activate the virtual environment (project root)**

Windows (PowerShell):
```
python -m venv .venv
.venv\Scripts\Activate.ps1
```
If PowerShell blocks it: `Set-ExecutionPolicy -Scope Process Bypass`, then activate again. Command Prompt: `.venv\Scripts\activate.bat`

Mac / Linux:
```
python3 -m venv .venv
source .venv/bin/activate
```
Then, with `(.venv)` showing in the prompt:
```
pip install -r requirements.txt
```
In VS Code press Ctrl+Shift+P > "Python: Select Interpreter" > choose the `.venv` one.

**Backend settings**
```
copy backend\.env.example backend\.env        (Mac/Linux: cp backend/.env.example backend/.env)
```
Change `SECRET_KEY` to any long random text. Leave `DATABASE_URL` out to use SQLite, or see section 3 for PostgreSQL.

**Frontend**
```
cd frontend
npm install
copy .env.example .env                        (Mac/Linux: cp .env.example .env)
cd ..
```

## 2. Run it (two terminals)

Terminal 1, backend (venv active):
```
python backend/seed.py                 # once: adds 48 sample students
cd backend
uvicorn app.main:app --reload --port 8000
```
Terminal 2, frontend:
```
cd frontend
npm run dev
```
Open http://localhost:5173. The SkillMesh logo appears, then the sign in / sign up popup after 2 seconds.
API documentation: http://localhost:8000/docs. Seeded test login: `u01@example.com` / `password123`.

Tests and evaluation (venv active, project root):
```
pytest backend
pytest ml
python ml/run_evaluation.py
```

## 3. Use PostgreSQL (as in the project abstract)

Create a database named `skillmesh` in PostgreSQL, then put this in `backend/.env`:
```
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/skillmesh
```
Tables are created automatically on startup. Run `python backend/seed.py` again to fill the new database.

## 4. Deploy (all free)

Database on **Neon**, backend on **Render**, frontend on **Vercel**. (Render's free PostgreSQL is deleted after 30 days, so Neon is used instead.)

1. **Push to GitHub:** `git add .`, `git commit -m "Ready for deploy"`, `git push`.
2. **Neon:** create a project at neon.com and copy its connection string (`postgresql://...?sslmode=require`).
3. **Render:** New > Web Service (not Blueprint) > pick the repo. Leave Root Directory empty.
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Environment: `DATABASE_URL` (Neon string), `SECRET_KEY` (long random text), `PYTHON_VERSION=3.12.3`,
     `CORS_ORIGINS` and `FRONTEND_URL` (your Vercel URL, set after step 5), `SHOW_RESET_LINK`.
   - Check `https://YOUR-API.onrender.com/health`.
4. **Sample data:** on your computer (venv active) run
   `$env:DATABASE_URL="NEON-STRING"` then `python backend/seed.py` (Mac/Linux: `DATABASE_URL="NEON-STRING" python backend/seed.py`).
5. **Vercel:** New Project > same repo > Root Directory `frontend` > environment variable `VITE_API_URL` = your Render URL (no trailing slash).
6. Put the Vercel URL into Render's `CORS_ORIGINS` and `FRONTEND_URL` (no trailing slash). Render redeploys by itself.

Free Render services sleep after 15 minutes without traffic, so the first request after a break takes about a minute.

## 4b. Forgot password (email reset link)

On the sign in screen, **Forgot password?** asks for the email and creates a one-time link (valid 30 minutes) that opens `/reset-password`.
- **While developing:** leave the `SMTP_*` values empty in `backend/.env`. The link then appears on the screen (and in the backend terminal), so you can test without email.
- **For real emails:** fill `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` in `backend/.env`. With Gmail, create an App Password at https://myaccount.google.com/apppasswords and use `smtp.gmail.com`, port `587`.
- **On Render:** set `FRONTEND_URL` to your Vercel URL, add the same `SMTP_*` variables, and set `SHOW_RESET_LINK=false`.

## 5. Team workflow (Git)

One repository, one branch per person (`feature/frontend`, `feature/backend`, `feature/ml`), merged to `main` with pull requests.
Each folder is independent: the frontend only needs the API URL, the backend only imports `get_top_matches`,
and the ML package can be developed and tested on its own with `pytest ml`.

## 6. Known limits and next steps
- The ML evaluation uses synthetic data. Collect real users for a real result.
- Replace TF-IDF with Sentence-BERT in `ml/skillmesh_ml/similarity.py`.
- Add Alembic migrations, email verification and password reset.
- Add real-time notifications (WebSockets) instead of polling.
