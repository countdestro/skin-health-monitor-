"""PostgreSQL schema — Section 7.4 (users, analysis_sessions, condition_predictions, recommendations)."""
from datetime import datetime
from sqlalchemy import String, Text, Float, Integer, BigInteger, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import uuid


def gen_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    email: Mapped[str | None] = mapped_column(Text, unique=True, nullable=True)
    display_name: Mapped[str | None] = mapped_column(Text, nullable=True)
    consent_given_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    analyses: Mapped[list["AnalysisSession"]] = relationship("AnalysisSession", back_populates="user", cascade="all, delete-orphan")


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=gen_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    image_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_s3_key: Mapped[str | None] = mapped_column(Text, nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    top_condition: Mapped[str | None] = mapped_column(Text, nullable=True)
    top_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    skin_health_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    severity_tier: Mapped[str | None] = mapped_column(Text, nullable=True)
    processing_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="analyses")
    condition_predictions: Mapped[list["ConditionPrediction"]] = relationship("ConditionPrediction", back_populates="session", cascade="all, delete-orphan")
    recommendations: Mapped[list["Recommendation"]] = relationship("Recommendation", back_populates="session", cascade="all, delete-orphan")


class ConditionPrediction(Base):
    __tablename__ = "condition_predictions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False)
    condition_name: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    class_id: Mapped[int] = mapped_column(Integer, nullable=False)

    session: Mapped["AnalysisSession"] = relationship("AnalysisSession", back_populates="condition_predictions")


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    session_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("analysis_sessions.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    priority_rank: Mapped[int] = mapped_column(Integer, nullable=False)

    session: Mapped["AnalysisSession"] = relationship("AnalysisSession", back_populates="recommendations")
