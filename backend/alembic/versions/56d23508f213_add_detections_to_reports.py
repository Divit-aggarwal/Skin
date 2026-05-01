"""add_detections_to_reports

Revision ID: 56d23508f213
Revises: 005
Create Date: 2026-05-01

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = '56d23508f213'
down_revision = '005'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'analysis_reports',
        sa.Column('detections', JSONB, nullable=False, server_default='[]')
    )


def downgrade() -> None:
    op.drop_column('analysis_reports', 'detections')
