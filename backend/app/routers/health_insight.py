"""POST /health-insight — compute SHS, severity, recommendations; persist to DB; return full analysis."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models import User, AnalysisSession, ConditionPrediction, Recommendation
from app.schemas import HealthInsightRequest, success_response, error_response, ConditionPrediction as CondSchema
from app.insight_engine import compute_skin_health_score, get_severity_tier, get_recommendations

router = APIRouter(tags=["health-insight"])


@router.post("/health-insight", response_model=None)
async def health_insight(
    body: HealthInsightRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Compute composite skin health score, severity tier, and recommendations.
    Persist analysis_sessions, condition_predictions, recommendations. Return full payload.
    """
    quality = body.quality_score or 1.0
    preds = [{"condition": p.condition, "confidence": p.confidence} for p in body.predictions]
    score = compute_skin_health_score(
        body.top_condition,
        body.top_confidence,
        quality_score=quality,
        predictions=preds,
    )
    tier, color = get_severity_tier(score)
    recs = get_recommendations(body.top_condition, body.top_confidence, score, preds)

    session = AnalysisSession(
        user_id=body.user_id,
        image_hash=body.image_hash,
        image_s3_key=body.image_s3_key,
        quality_score=quality,
        top_condition=body.top_condition,
        top_confidence=body.top_confidence,
        skin_health_score=score,
        severity_tier=tier,
        processing_time_ms=body.processing_time_ms or 0,
    )
    db.add(session)
    await db.flush()

    for p in body.predictions:
        db.add(ConditionPrediction(
            session_id=session.id,
            condition_name=p.condition,
            confidence=p.confidence,
            class_id=p.class_id,
        ))
    for r in recs:
        db.add(Recommendation(
            session_id=session.id,
            category=r["category"],
            content=r["content"],
            priority_rank=r["priority_rank"],
        ))
    await db.commit()

    return success_response({
        "analysis_id": session.id,
        "skin_health_score": score,
        "severity_tier": tier,
        "severity_color": color,
        "top_condition": body.top_condition,
        "top_confidence": body.top_confidence,
        "conditions": [{"condition": p.condition, "confidence": p.confidence, "class_id": p.class_id} for p in body.predictions],
        "recommendations": recs,
        "processing_time_ms": body.processing_time_ms or 0,
        "created_at": session.created_at.isoformat() + "Z",
    }, message="Analysis complete")
