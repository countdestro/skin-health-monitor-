"""
Image Processing stub (Member 2 placeholder).
Passes through the image as 'processed' so the full pipeline can run without face detection.
Replace with real OpenCV/MediaPipe pipeline when available.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Image Processing (stub)", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProcessRequest(BaseModel):
    image_b64: str
    session_id: str | None = None


@app.get("/health")
def health():
    return {"status": "ok", "module": "image_processor"}


@app.post("/process-image")
def process_image(body: ProcessRequest):
    """Pass-through: return same image as processed_image_b64 with quality_score 1.0."""
    if not body.image_b64 or len(body.image_b64) < 100:
        raise HTTPException(status_code=422, detail="Invalid or empty image_b64")
    return {
        "success": True,
        "processed_image_b64": body.image_b64,
        "quality_score": 1.0,
        "data": {
            "processed_image_b64": body.image_b64,
            "quality_score": 1.0,
        },
    }
