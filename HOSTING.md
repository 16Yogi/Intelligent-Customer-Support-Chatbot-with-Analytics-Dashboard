# How to Host This Project

You can run the **Customer Support Chatbot** (frontend + backend + PostgreSQL) in several ways.

---

## Option 1: Docker Compose (single server / VPS)

Best for: your own server, VPS (DigitalOcean, AWS EC2, Linode, etc.), or a machine with Docker.

### 1. Install Docker and Docker Compose

- **Windows**: [Docker Desktop](https://docs.docker.com/desktop/install/windows-install/)
- **Linux**: `curl -fsSL https://get.docker.com | sh` then install [Compose](https://docs.docker.com/compose/install/)

### 2. Build and run

From the **project root** (where `docker-compose.yml` is):

```bash
docker compose up --build -d
```

- **App (frontend + API):** http://localhost:3000  
  - The UI is served here; `/api` is proxied to the backend.
- **Backend only:** http://localhost:8000 (optional, for health checks).
- **PostgreSQL:** localhost:5432 (user `chatbot`, password `chatbot`, DB `chatbot_db`).

### 3. Production tips on a VPS

- Use **HTTPS**: put Nginx or Caddy in front and add SSL (e.g. Let’s Encrypt).
- **Strong DB password**: set `POSTGRES_PASSWORD` (and optionally user/DB) via environment or a `.env` file and do **not** commit secrets.
- **Restrict ports**: e.g. expose only 80/443 and 22; don’t expose 5432 publicly.

---

## Option 2: Railway / Render (managed hosting)

Good for: quick deploy without managing a server.

### Railway

1. Push the project to **GitHub**.
2. In [Railway](https://railway.app): New Project → Deploy from GitHub → select this repo.
3. Add services:
   - **PostgreSQL**: add from Railway’s “New” → Database.
   - **Backend**: add a service, set root to the repo, set **Build Command** to use the backend (e.g. `pip install -r backend/requirements.txt` and copy app + dataset), **Start Command** e.g. `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Set `DATABASE_URL` from the Postgres service.
   - **Frontend**: add another service; set build to `cd frontend && npm install && npm run build`, and serve the `frontend/dist` folder (e.g. with `npx serve -s dist`). Set `VITE_API_URL` to the backend’s public URL (e.g. `https://your-backend.up.railway.app`) so the built app calls the correct API.
4. Open the frontend URL Railway gives you.

### Render

- **Web Service (backend):** connect repo, root = project root; build: install Python deps, copy `backend`; start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Add a **PostgreSQL** database and set `DATABASE_URL`.
- **Static Site (frontend):** build command e.g. `cd frontend && npm install && npm run build`; publish `frontend/dist`. Set **Environment**: `VITE_API_URL=https://your-backend.onrender.com`.
- Use the frontend URL as the app URL.

---

## Option 3: Frontend and backend separately

- **Frontend:** build with `cd frontend && npm run build`. Deploy the `frontend/dist` folder to **Vercel**, **Netlify**, or any static host. Set `VITE_API_URL` to your backend URL (e.g. `https://api.yourdomain.com`) in the build environment.
- **Backend:** run the FastAPI app (e.g. on Railway, Render, Fly.io, or a VPS) with PostgreSQL. Enable CORS for the frontend origin. Use the same backend URL as `VITE_API_URL`.

---

## Environment variables

| Variable           | Where        | Purpose |
|--------------------|--------------|--------|
| `DATABASE_URL`     | Backend      | Postgres connection string (e.g. `postgresql+psycopg2://user:pass@host:5432/db`). Omit for local SQLite. |
| `VITE_API_URL`     | Frontend build | Backend base URL (e.g. `https://api.example.com`). Leave unset for local dev (`http://localhost:8000`). Set to `""` when using same-origin `/api` (e.g. Docker nginx proxy). |

---

## Quick recap

- **Local dev:** run backend (`uvicorn app.main:app --reload --port 8000`) and frontend (`npm run dev` in `frontend/`). No Docker needed; backend can use SQLite.
- **Single server:** `docker compose up --build -d` → open http://localhost:3000.
- **Cloud:** use Railway/Render (or similar) with Postgres + backend + frontend, and set `VITE_API_URL` to the deployed backend URL.
