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

## 4. Deploy (free tiers)

**Push to GitHub first**
```
git init
git add .
git commit -m "SkillMesh"
git branch -M main
git remote add origin https://github.com/YOUR-USER/skillmesh.git
git push -u origin main
```

**Backend + database on Render**
1. render.com > New > Blueprint > pick your repo. It reads `render.yaml` and creates the API and a PostgreSQL database.
2. After the first deploy, open the service > Environment and set `CORS_ORIGINS` to your Vercel URL (step below). Redeploy.
3. Copy the API URL, for example `https://skillmesh-api.onrender.com`. Check `/health`.
4. Optional sample data: Render shell > `python backend/seed.py`.

**Frontend on Vercel**
1. vercel.com > Add New > Project > pick the repo, set **Root Directory** to `frontend` (Vite is detected automatically).
2. Add environment variable `VITE_API_URL` = your Render API URL (no trailing slash). Deploy.
3. Put the Vercel URL into Render's `CORS_ORIGINS`.

Free Render services sleep when idle, so the first request after a break can take about 30 seconds.

## 5. Team workflow (Git)

One repository, one branch per person (`feature/frontend`, `feature/backend`, `feature/ml`), merged to `main` with pull requests.
Each folder is independent: the frontend only needs the API URL, the backend only imports `get_top_matches`,
and the ML package can be developed and tested on its own with `pytest ml`.

## 6. Known limits and next steps
- The ML evaluation uses synthetic data. Collect real users for a real result.
- Replace TF-IDF with Sentence-BERT in `ml/skillmesh_ml/similarity.py`.
- Add Alembic migrations, email verification and password reset.
- Add real-time notifications (WebSockets) instead of polling.
