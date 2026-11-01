# Frontend and UI (Ruchika)

React 18 + Vite + React Router + Axios.

| Path | Purpose |
|---|---|
| `src/pages/Landing.jsx` | splash with logo, sign in / sign up popup after 2 seconds |
| `src/pages/Setup.jsx` | first-time profile requirements |
| `src/pages/Discover.jsx` | mesh graph + recommended peers + profile panel |
| `src/pages/Requests.jsx`, `Sessions.jsx` | incoming/outgoing requests; schedule, complete and give feedback |
| `src/pages/HowItWorks.jsx` | weight sliders, similarity tester, SkillMesh vs keyword chart |
| `src/components/` | Navbar, MeshGraph, PeerCard, SkillInput, AvailabilityGrid, ProfileForm, Toast, Logo |
| `src/AuthContext.jsx`, `src/api.js` | JWT login state, Axios instance |
| `src/styles.css` | the whole design (colors are CSS variables at the top) |

Run:
```
cd frontend
npm install
npm run dev        # http://localhost:5173  (the backend must be running on port 8000)
npm run build      # production build in dist/
```
