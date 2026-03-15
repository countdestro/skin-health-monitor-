"""POST /auth/session — create anonymous or authenticated session, return JWT."""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.models import User
from app.schemas import SessionCreate, success_response, error_response, APIResponse
from app.auth import create_access_token
from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()


@router.post("/session", response_model=None)
async def create_session(
    body: SessionCreate,
    db: AsyncSession = Depends(get_db),
):
    """Create anonymous or authenticated user session. Returns JWT and session_id (user_id)."""
    from uuid import uuid4
    user_id = str(uuid4())
    user = User(
        id=user_id,
        email=body.email,
        display_name=body.display_name,
        consent_given_at=datetime.utcnow() if body.consent_given else None,
    )
    db.add(user)
    await db.flush()
    token = create_access_token(user_id)
    expires_at = datetime.utcnow()
    from datetime import timedelta
    expires_at = expires_at + timedelta(minutes=settings.jwt_expire_minutes)
    return success_response({
        "session_id": user_id,
        "user_id": user_id,
        "token": token,
        "expires_at": expires_at.isoformat() + "Z",
    }, message="Session created")
