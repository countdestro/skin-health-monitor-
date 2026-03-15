# Member 3 – AI Skin Disease Classification

**Role (from workflow):** Skin disease classification model — CNN (MobileNetV2) → classification → Acne, Eczema, Psoriasis, Rosacea, Pigmentation.

## Setup

```bash
cd skin_health_monitor_member3
pip install -r requirements.txt
```

## Run prediction API

```bash
# Optional: point to trained weights
set SKIN_MODEL_WEIGHTS=C:\path\to\skin_model.weights.h5

cd api
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

- `GET /health` — health check  
- `POST /predict` — form field `file` = image (output from Member 2’s pipeline)

Example:

```bash
curl -X POST "http://127.0.0.1:8001/predict" -F "file=@processed_face.jpg"
```

## Train (HAM10000 / DermNet / custom — map to 5 class folder names)

Folder layout:

```
data/
  Acne/
  Eczema/
  Psoriasis/
  Rosacea/
  Pigmentation/
```

```bash
python scripts/train.py --data_dir "C:/path/to/data" --epochs 15 --out weights/skin_model.weights.h5
```

After training, set `SKIN_MODEL_WEIGHTS` or place weights at `weights/skin_model.weights.h5`.

## Integration

- **Input:** RGB image (224×224 ideal; any size is resized) — preferably face/skin crop from Member 2.  
- **Output:** JSON for Member 4 (`/health-insight`) — use `condition`, `confidence`, `all_scores`.

## Git — push to GitHub

Repo is initialized on `main`. To publish:

1. Create an **empty** repository on [GitHub](https://github.com/new) (no README/license).
2. In PowerShell:

```powershell
cd "C:\Users\Karthik B V\skin_health_monitor_member3"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

Sign in when prompted (browser or Personal Access Token). To fix author for commits:  
`git config user.email "you@example.com"` and `git config user.name "Your Name"`.

## Disclaimer

Not for clinical or diagnostic use. Demo / hackathon only.
