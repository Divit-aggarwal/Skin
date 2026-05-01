import uuid

from sqlalchemy import Float, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import TimestampMixin


class AnalysisReport(TimestampMixin, Base):
    __tablename__ = "analysis_reports"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_sessions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    acne_score: Mapped[float] = mapped_column(Float, nullable=False)
    wrinkle_score: Mapped[float] = mapped_column(Float, nullable=False)
    oiliness_score: Mapped[float] = mapped_column(Float, nullable=False)
    overall_score: Mapped[float] = mapped_column(Float, nullable=False)
    severity_level: Mapped[str] = mapped_column(String(20), nullable=False)
    blur_score: Mapped[float] = mapped_column(Float, nullable=False)
    face_count: Mapped[int] = mapped_column(Integer, nullable=False)
    zone_breakdown: Mapped[list] = mapped_column(JSONB, nullable=False)
    yolo_detections: Mapped[list] = mapped_column(JSONB, nullable=False)
    model_version: Mapped[str] = mapped_column(String(100), nullable=False)
