import uuid

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.base import SoftDeleteMixin, TimestampMixin


class Image(TimestampMixin, SoftDeleteMixin, Base):
    __tablename__ = "images"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    mime_type: Mapped[str] = mapped_column(String(50), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    blur_score: Mapped[float] = mapped_column(Float, nullable=False)
    face_count: Mapped[int] = mapped_column(Integer, nullable=False)
    quality_passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    quality_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
