"""
REST API for Module 3 – POST /predict
Accepts processed skin/face image: multipart file or JSON { processed_image_b64 }.
JSON mode used by backend gateway (Member 4).
"""

from __future__ import annotations

import base64
import os
import sys
import time

# Add project root
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.classifier import SKIN_CONDITIONS
from src.inference import load_trained_weights, predict_image_bytes

app = FastAPI(
    title="AI Skin Disease Detection (Member 3)",
    description="MobileNetV2 classifier – Acne, Eczema, Psoriasis, Rosacea, Pigmentation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    w = os.environ.get("SKIN_MODEL_WEIGHTS")
    load_trained_weights(w)


@app.get("/health")
def health():
    return {"status": "ok", "module": "ai_skin_predict"}


class PredictRequest(BaseModel):
    """Gateway (Member 4) sends processed image as base64."""
    processed_image_b64: str


def _to_gateway_response(result: dict, inference_time_ms: int) -> dict:
    """Shape expected by backend analyse gateway."""
    frac = result.get("confidence_fraction", result["confidence"] / 100.0)
    all_scores = result.get("all_scores", [])
    # Backend condition IDs: 1–7 for HAM10000 classes (Actinic keratosis … Vascular lesion)
    predictions = [
        {"condition": s["condition"], "confidence": s["probability"], "class_id": SKIN_CONDITIONS.index(s["condition"]) + 1}
        for s in all_scores
    ]
    return {
        "top_condition": result["condition"],
        "top_confidence": frac,
        "predictions": predictions,
        "inference_time_ms": inference_time_ms,
    }


@app.post("/predict")
async def predict(body: PredictRequest | None = None, file: UploadFile = File(None)):
    """
    Either: multipart form field `file` = image, or JSON body { "processed_image_b64": "..." }.
    JSON used by backend gateway. Returns gateway shape when called with JSON.
    """
    if body is not None and body.processed_image_b64:
        try:
            data = base64.b64decode(body.processed_image_b64)
        except Exception as e:
            raise HTTPException(400, f"Invalid base64: {e!s}") from e
        if len(data) < 100:
            raise HTTPException(400, "Empty or invalid image")
        t0 = time.perf_counter()
        result = predict_image_bytes(data)
        inference_time_ms = int((time.perf_counter() - t0) * 1000)
        return _to_gateway_response(result, inference_time_ms)

    if file is None:
        raise HTTPException(400, "Provide either multipart file or JSON body with processed_image_b64")
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "Upload an image file (image/jpeg or image/png)")
    data = await file.read()
    if len(data) < 100:
        raise HTTPException(400, "Empty or invalid image")
    try:
        result = predict_image_bytes(data)
    except Exception as e:
        raise HTTPException(422, f"Prediction failed: {e!s}") from e
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
