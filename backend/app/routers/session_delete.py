"""DELETE /session/{session_id} — delete session and associated image from storage."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.database import get_db
from app.models import AnalysisSession
from app.schemas import success_response

router = APIRouter(tags=["session"])


@router.delete("/session/{session_id}", response_model=None)
async def delete_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Delete analysis session and associated records (cascade). Optionally remove image from storage."""
    q = select(AnalysisSession).where(AnalysisSession.id == session_id)
    result = await db.execute(q)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    await db.delete(session)
    await db.commit()
    # TODO: if image_s3_key set, delete from S3; if local, delete file
    return success_response({"deleted": session_id}, message="Session deleted")
