"""Pydantic request/response schemas and standard API envelope."""
from typing import Any, Optional
from pydantic import BaseModel
from datetime import datetime


# ---------- Standard response envelope (Section 8.3) ----------
class APIResponse(BaseModel):
    success: bool = True
    code: str = "OK"
    message: str = "Success"
    data: Optional[dict[str, Any]] = None


def success_response(data: dict, message: str = "Success") -> dict:
    return {"success": True, "code": "OK", "message": message, "data": data}


def error_response(code: str, message: str, data: Optional[dict] = None) -> dict:
    return {"success": False, "code": code, "message": message, "data": data or {}}


# ---------- Auth ----------
class SessionCreate(BaseModel):
    email: Optional[str] = None
    display_name: Optional[str] = None
    consent_given: bool = True


class SessionResponse(BaseModel):
    session_id: str
    user_id: str
    token: str
    expires_at: datetime


# ---------- Analyse (gateway) ----------
class AnalyseRequest(BaseModel):
    image_b64: str
    session_id: str
    timestamp: Optional[str] = None


# ---------- Health insight (internal + external) ----------
class ConditionPrediction(BaseModel):
    condition: str
    confidence: float
    class_id: int


class HealthInsightRequest(BaseModel):
    session_id: str
    user_id: str
    predictions: list[ConditionPrediction]
    top_condition: str
    top_confidence: float
    quality_score: Optional[float] = 1.0
    processing_time_ms: Optional[int] = 0
    image_hash: Optional[str] = None
    image_s3_key: Optional[str] = None


class RecommendationItem(BaseModel):
    category: str
    content: str
    priority_rank: int


class HealthInsightResponse(BaseModel):
    analysis_id: str
    skin_health_score: int
    severity_tier: str
    severity_color: str
    top_condition: str
    top_confidence: float
    conditions: list[ConditionPrediction]
    recommendations: list[RecommendationItem]
    processing_time_ms: int
    created_at: datetime
