import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ImageUploadRequest(BaseModel):
    image_data: str
    mime_type: str


class ImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    mime_type: str
    size_bytes: int
    blur_score: float
    face_count: int
    quality_passed: bool
    quality_reason: str | None
    created_at: datetime
