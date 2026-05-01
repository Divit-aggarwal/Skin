"""recommendations

Revision ID: 005
Revises: 004
Create Date: 2026-04-24
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recommendations",
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
        ),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("text", sa.String(500), nullable=False),
        sa.Column("priority", sa.Integer, nullable=False),
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
    op.create_index("ix_recommendations_session_id", "recommendations", ["session_id"])


def downgrade() -> None:
    op.drop_table("recommendations")
