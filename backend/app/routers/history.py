"""GET /history/{user_id} — paginated past analysis sessions. GET /session/{session_id} — full detail."""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models import User, AnalysisSession, ConditionPrediction, Recommendation
from app.schemas import success_response, error_response

router = APIRouter(tags=["history"])


@router.get("/history/{user_id}", response_model=None)
async def get_history(
    user_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Return paginated list of past analysis sessions for user."""
    offset = (page - 1) * page_size
    q = select(AnalysisSession).where(AnalysisSession.user_id == user_id).order_by(desc(AnalysisSession.created_at)).offset(offset).limit(page_size)
    result = await db.execute(q)
    sessions = result.scalars().all()
    items = [
        {
            "id": s.id,
            "created_at": s.created_at.isoformat() + "Z",
            "skin_health_score": s.skin_health_score,
            "top_condition": s.top_condition,
            "top_confidence": s.top_confidence,
            "severity_tier": s.severity_tier,
        }
        for s in sessions
    ]
    return success_response({
        "user_id": user_id,
        "sessions": items,
        "page": page,
        "page_size": page_size,
    })


@router.get("/session/{session_id}", response_model=None)
async def get_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Return full detail for a single analysis session."""
    q = select(AnalysisSession).where(AnalysisSession.id == session_id)
    result = await db.execute(q)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    qc = select(ConditionPrediction).where(ConditionPrediction.session_id == session_id)
    qr = select(Recommendation).where(Recommendation.session_id == session_id)
    conds = (await db.execute(qc)).scalars().all()
    recs = (await db.execute(qr)).scalars().all()
    return success_response({
        "id": session.id,
        "user_id": session.user_id,
        "created_at": session.created_at.isoformat() + "Z",
        "skin_health_score": session.skin_health_score,
        "severity_tier": session.severity_tier,
        "top_condition": session.top_condition,
        "top_confidence": session.top_confidence,
        "quality_score": session.quality_score,
        "processing_time_ms": session.processing_time_ms,
        "conditions": [{"condition_name": c.condition_name, "confidence": c.confidence, "class_id": c.class_id} for c in conds],
        "recommendations": [{"category": r.category, "content": r.content, "priority_rank": r.priority_rank} for r in recs],
    })
