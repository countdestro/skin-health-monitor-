# AI Skin Health Monitor — Integrated Stack

Full pipeline: **Frontend (Next.js)** → **Backend (8000)** → **Image processor (8001)** → **AI inference (8002)** → health insight & DB.

## Contents

| Folder | Role |
|--------|------|
| `frontend/` | Next.js app (weal) — capture, results, history; calls `POST /analyse` on backend |
| `backend/` | FastAPI gateway, auth, health-insight, history, DB (Member 4) |
| `image_processor/` | Stub (Member 2 placeholder) — pass-through so pipeline runs; replace with real face/skin preprocessing |
| `ai_inference/` | Member 3 — MobileNetV2 skin disease classifier; `POST /predict` (file or JSON base64) |

- **Standalone test page:** `frontend/public/index-standalone.html` — talks to image processor on port 8001 (open in browser after starting services).

## Quick start (Docker)

1. Copy env and run stack:
   ```bash
   cp .env.example .env
   docker compose up --build
   ```
2. Run DB migrations:
   ```bash
   docker compose exec backend alembic upgrade head
   ```
3. Frontend (separate terminal):
   ```bash
   cd frontend && npm install && npm run dev
   ```
   Open http://localhost:3000. Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local` if needed.

## Ports

| Port | Service |
|------|---------|
| 3000 | Next.js (when run with `npm run dev`) |
| 8000 | Backend API |
| 8001 | Image processor |
| 8002 | AI inference (Member 3) |
| 5432 | PostgreSQL |
| 6379 | Redis |

## Run without Docker

1. **Backend:** PostgreSQL + Redis running; then `cd backend`, `pip install -r requirements.txt`, `alembic upgrade head`, `uvicorn app.main:app --port 8000`.
2. **Image processor:** `cd image_processor`, `pip install -r requirements.txt`, `uvicorn app.main:app --port 8001`.
3. **AI inference:** `cd ai_inference`, `pip install -r requirements.txt`, `uvicorn api.main:app --port 8002` (from `ai_inference` dir).
4. **Frontend:** `cd frontend`, `npm install`, `npm run dev`.

Set `.env` (or env vars) so `IMAGE_PROCESSOR_URL=http://localhost:8001` and `AI_INFERENCE_URL=http://localhost:8002`.

## Disclaimer

For demo / hackathon only. Not for clinical or diagnostic use.
