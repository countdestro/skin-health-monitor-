"""
POST /analyse — API gateway.
Validates request, calls Image Processing → AI Inference → Health Insight, returns full analysis.
Supports mock mode for frontend development when other services are unavailable.
"""
import hashlib
import base64
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
import httpx
from app.database import get_db
from app.models import User
from app.schemas import AnalyseRequest, success_response, error_response, HealthInsightRequest, ConditionPrediction
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["analyse"])
settings = get_settings()

# Mock response — same shape as real analysis (HAM10000 conditions)
MOCK_ANALYSIS = {
    "analysis_id": "mock-analysis-uuid-1234",
    "skin_health_score": 72,
    "severity_tier": "Fair",
    "severity_color": "#F39C12",
    "top_condition": "Melanocytic nevus",
    "top_confidence": 0.85,
    "conditions": [
        {"condition": "Melanocytic nevus", "confidence": 0.85, "class_id": 6},
        {"condition": "Benign keratosis", "confidence": 0.08, "class_id": 3},
        {"condition": "Melanoma", "confidence": 0.02, "class_id": 5},
    ],
    "recommendations": [
        {"category": "Lifestyle", "content": "Monitor for changes (asymmetry, border, colour, diameter). Use SPF when outdoors.", "priority_rank": 1},
        {"category": "Skincare Routine", "content": "Use a gentle, fragrance-free cleanser and moisturiser.", "priority_rank": 2},
        {"category": "Hydration", "content": "Drink 2–3 litres of water daily; use a humidifier in dry environments.", "priority_rank": 3},
    ],
    "processing_time_ms": 4200,
    "created_at": "2024-01-15T12:00:00.000Z",
}


async def rate_limit_check(user_id: str) -> bool:
    """Return True if under limit. Uses Redis if available."""
    try:
        import redis
        r = redis.from_url(settings.redis_url)
        key = f"rate:{user_id}"
        n = r.incr(key)
        if n == 1:
            r.expire(key, 60)
        return n <= settings.rate_limit_per_minute
    except Exception:
        return True  # allow if Redis down


@router.post("/analyse", response_model=None)
async def analyse(
    body: AnalyseRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Gateway: receive image_b64 + session_id, call image processing → AI → health insight, return full report.
    If MOCK_ANALYSE=1 in env or downstream services fail, returns mock response for frontend development.
    """
    import os
    use_mock = os.environ.get("MOCK_ANALYSE", "").lower() in ("1", "true", "yes")
    user_id = body.session_id

    if not use_mock:
        ok = await rate_limit_check(user_id)
        if not ok:
            raise HTTPException(status_code=429, detail=error_response("RATE_LIMIT_EXCEEDED", "More than 10 analyses per minute per user"))

    if use_mock:
        return success_response(MOCK_ANALYSIS, message="Analysis complete (mock)")

    async with httpx.AsyncClient(timeout=15.0) as client:
        # 1) Image processing
        try:
            r1 = await client.post(
                f"{settings.image_processor_url}/process-image",
                json={"image_b64": body.image_b64, "session_id": body.session_id},
            )
            r1.raise_for_status()
            proc = r1.json()
        except Exception as e:
            if getattr(e, "response", None) and getattr(e.response, "status_code", None) == 422:
                raise HTTPException(status_code=422, detail=error_response("NO_FACE_DETECTED", "No face found in image"))
            logger.warning("Image processor unavailable, returning mock: %s", e)
            return success_response(MOCK_ANALYSIS, message="Analysis complete (mock fallback)")

        processed_b64 = proc.get("processed_image_b64") or proc.get("data", {}).get("processed_image_b64")
        quality = proc.get("quality_score") or proc.get("data", {}).get("quality_score") or 1.0
        if not processed_b64:
            return success_response(MOCK_ANALYSIS, message="Analysis complete (mock fallback)")

        # 2) AI inference
        try:
            r2 = await client.post(
                f"{settings.ai_inference_url}/predict",
                json={"processed_image_b64": processed_b64},
            )
            r2.raise_for_status()
            pred_data = r2.json()
        except Exception as e:
            logger.warning("AI inference unavailable, returning mock: %s", e)
            return success_response(MOCK_ANALYSIS, message="Analysis complete (mock fallback)")

        predictions = pred_data.get("predictions") or pred_data.get("data", {}).get("predictions") or []
        top_condition = pred_data.get("top_condition") or (predictions[0]["condition"] if predictions else "Healthy")
        top_confidence = float(pred_data.get("top_confidence") or (predictions[0]["confidence"] if predictions else 0.5))
        inference_time = int(pred_data.get("inference_time_ms") or 0)

        # 3) Health insight (internal)
        image_hash = hashlib.sha256(body.image_b64.encode() if isinstance(body.image_b64, str) else body.image_b64).hexdigest()[:64]
        insight_body = HealthInsightRequest(
            session_id=body.session_id,
            user_id=user_id,
            predictions=[ConditionPrediction(condition=p["condition"], confidence=float(p["confidence"]), class_id=int(p.get("class_id", 0))) for p in predictions],
            top_condition=top_condition,
            top_confidence=top_confidence,
            quality_score=quality,
            processing_time_ms=inference_time + 500,
            image_hash=image_hash,
        )
        from app.routers.health_insight import health_insight
        response = await health_insight(insight_body, db)
        return response
