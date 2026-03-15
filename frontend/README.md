# AI Skin Health Monitor — Frontend (Member 1)

React/Next.js frontend for the AI Skin Health Monitor: camera/upload UI, client-side validation, API orchestration, and results dashboard.

## Stack

- **React 18** + **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **Zustand** (session state)
- **TanStack Query** (API state)
- **Recharts** (charts)
- **react-webcam** (camera capture)

## Setup

1. **Install Node.js** (v18+) and npm if not already installed. Ensure `node` and `npm` are on your PATH.

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Environment:** Copy `.env.example` to `.env` and set `NEXT_PUBLIC_API_URL` if the backend is not at `http://localhost:8000`.

4. **Run development server:**

   ```bash
   npm run dev
   ```

   Open [http://localhost:3000](http://localhost:3000).

## Member 1 Deliverables

- **App load & consent** — Privacy consent modal; session UUID in localStorage (Zustand persist).
- **Capture screen** — Tabs: Live Camera, Upload Photo; face-alignment overlay; capture/upload flow.
- **Client-side validation** — MIME (JPEG/PNG/WebP), size ≤10 MB, resolution ≥224×224 px.
- **API submission** — Image compressed to max 800×800, base64, POST to backend `/analyse`; loading screen with “Detecting face…”, “Analysing skin…”, “Generating insights…”.
- **Results dashboard** — Score gauge (0–100, colour zones), conditions bar chart (>10%), severity badge, expandable recommendations, history chart when ≥2 sessions.
- **Error handling** — Camera denied (fallback to upload), timeout (retry message), no face (422), low confidence message, server errors.

## API contract

- **POST** `/analyse` — Body: `{ image_b64, session_id, timestamp }`. Returns analysis with `analysis_id`, score, severity, predictions, recommendations.
- **GET** `/session/:id` — Full analysis for result page.
- **GET** `/history/:user_id` — Past sessions for history chart.

Backend is expected at `NEXT_PUBLIC_API_URL` (default `http://localhost:8000`).

## Push to GitHub (skin-health-monitor repo)

The repo [countdestro/skin-health-monitor-](https://github.com/countdestro/skin-health-monitor-) already has Member 3’s code. Add this frontend as a **`frontend/`** subfolder so both stay in one repo.

**Option A — Add frontend to the existing repo (recommended)**

In PowerShell (or Git Bash), run:

```powershell
# 1. Clone the repo
cd C:\Users\KAUSTUBH\Documents
git clone https://github.com/countdestro/skin-health-monitor-.git skin-health-monitor
cd skin-health-monitor

# 2. Copy this project into a frontend folder (all files/folders from weal)
#    Either copy the weal folder contents into a new "frontend" folder:
mkdir frontend
Copy-Item -Path "C:\Users\KAUSTUBH\Documents\weal\*" -Destination ".\frontend" -Recurse -Force

# 3. Commit and push
git add frontend
git commit -m "Add Member 1 frontend - Next.js skin health UI"
git push origin main
```

**Option B — This folder is already the only content you want in the repo**

If you are fine replacing the repo contents with only this frontend:

```powershell
cd C:\Users\KAUSTUBH\Documents\weal
git init
git add .
git commit -m "Member 1 frontend - AI Skin Health Monitor"
git branch -M main
git remote add origin https://github.com/countdestro/skin-health-monitor-.git
git push -u origin main --force
```

`--force` overwrites the existing `main` branch; only use if you intend to replace the current repo content.

## Scripts

- `npm run dev` — Start dev server
- `npm run build` — Production build
- `npm run start` — Start production server
- `npm run lint` — Run ESLint
- `npm run test` — Run Jest tests
