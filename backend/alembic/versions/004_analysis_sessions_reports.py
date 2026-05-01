"""analysis_sessions and analysis_reports

Revision ID: 004
Revises: 003
Create Date: 2026-04-24
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "analysis_sessions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "image_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("images.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("deleted_at", sa.TIMESTAMP(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_analysis_sessions_user_created",
        "analysis_sessions",
        ["user_id", "created_at"],
    )

    op.create_table(
        "analysis_reports",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("analysis_sessions.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("acne_score", sa.Float, nullable=False),
        sa.Column("wrinkle_score", sa.Float, nullable=False),
        sa.Column("oiliness_score", sa.Float, nullable=False),
        sa.Column("overall_score", sa.Float, nullable=False),
        sa.Column("severity_level", sa.String(20), nullable=False),
        sa.Column("blur_score", sa.Float, nullable=False),
        sa.Column("face_count", sa.Integer, nullable=False),
        sa.Column("zone_breakdown", postgresql.JSONB, nullable=False),
        sa.Column("yolo_detections", postgresql.JSONB, nullable=False),
        sa.Column("model_version", sa.String(100), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("analysis_reports")
    op.drop_table("analysis_sessions")
