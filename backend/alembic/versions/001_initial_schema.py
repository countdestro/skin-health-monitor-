"""Initial schema: users, analysis_sessions, condition_predictions, recommendations.

Revision ID: 001
Revises:
Create Date: 2024-01-15

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("display_name", sa.Text(), nullable=True),
        sa.Column("consent_given_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "analysis_sessions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("image_hash", sa.Text(), nullable=True),
        sa.Column("image_s3_key", sa.Text(), nullable=True),
        sa.Column("quality_score", sa.Float(), nullable=True),
        sa.Column("top_condition", sa.Text(), nullable=True),
        sa.Column("top_confidence", sa.Float(), nullable=True),
        sa.Column("skin_health_score", sa.Integer(), nullable=True),
        sa.Column("severity_tier", sa.Text(), nullable=True),
        sa.Column("processing_time_ms", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analysis_sessions_user_id"), "analysis_sessions", ["user_id"], unique=False)

    op.create_table(
        "condition_predictions",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("condition_name", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("class_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["analysis_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_condition_predictions_session_id"), "condition_predictions", ["session_id"], unique=False)

    op.create_table(
        "recommendations",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.UUID(), nullable=False),
        sa.Column("category", sa.Text(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("priority_rank", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["analysis_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recommendations_session_id"), "recommendations", ["session_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_recommendations_session_id"), table_name="recommendations")
    op.drop_table("recommendations")
    op.drop_index(op.f("ix_condition_predictions_session_id"), table_name="condition_predictions")
    op.drop_table("condition_predictions")
    op.drop_index(op.f("ix_analysis_sessions_user_id"), table_name="analysis_sessions")
    op.drop_table("analysis_sessions")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
