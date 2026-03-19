# ChatHub — Frontend

React frontend for the **Intelligent Customer Support Chatbot**: AI Chat and an analytics dashboard with real-time metrics.

## Tech stack

- **React 19** + **TypeScript**
- **Vite 6** (build tool)
- **Tailwind CSS** (styling)
- **Framer Motion** (animations)
- **Lucide React** (icons)
- **Recharts** (dashboard charts)
- **Axios** (API calls)

## Prerequisites

- **Node.js** 18+ (recommended: 20+)

## Setup

1. **Install dependencies**

   ```bash
   npm install
   ```

2. **Environment (optional)**

   - Create `.env` or `.env.local` in the `frontend` folder if you need to override the API URL.
   - **`VITE_API_URL`** — Backend base URL. If unset, the app uses `http://localhost:8000`. For production, set this to your deployed backend URL (e.g. `https://api.yourdomain.com`).

3. **Run the backend**

   The frontend expects the backend API to be running (see the main project or `backend/` README). Default: `http://localhost:8000`.

## Scripts

| Command        | Description                          |
|----------------|--------------------------------------|
| `npm run dev`  | Start dev server (Express + Vite) on port **3000** |
| `npm run build`| Production build → `dist/`           |
| `npm run preview` | Preview production build locally  |
| `npm run lint` | Type-check with TypeScript           |

## Run locally

```bash
npm install
npm run dev
```

Then open **http://localhost:3000**.

- **AI Chat** — Talk to the support bot (messages go to `POST /api/chat`).
- **Dashboard** — View analytics (data from `GET /api/analytics`).

## Project structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Chat.tsx       # Chat UI and message list
│   │   └── Dashboard.tsx  # Analytics charts and stats
│   ├── config.ts          # API base URL (VITE_API_URL)
│   ├── App.tsx            # Layout, sidebar, routing between Chat / Dashboard
│   ├── main.tsx
│   └── index.css
├── index.html
├── package.json
├── server.ts              # Dev server (Express + Vite middleware)
├── nginx.conf             # Production: serve static + proxy /api to backend
└── Dockerfile             # Production: build + nginx
```

## Production build

- **Build:** `npm run build` → output in `dist/`.
- **Deploy:** Serve the `dist/` folder with any static host (e.g. Nginx, Vercel, Netlify). Set **`VITE_API_URL`** at build time to your backend URL.
- **Docker:** Use the repo root `docker compose up` so the frontend is built and served with Nginx and `/api` is proxied to the backend.
