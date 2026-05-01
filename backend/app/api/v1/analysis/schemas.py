import uuid
from datetime import datetime

from pydantic import BaseModel


class SessionCreateRequest(BaseModel):
    image_id: uuid.UUID
    image_data: str  # base64 image bytes — Phase 1 only; Phase 2 pulls from S3


class ZoneScoreOut(BaseModel):
    zone: str
    score: float


class ReportOut(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    acne_score: float
    wrinkle_score: float
    oiliness_score: float
    overall_score: float
    severity_level: str
    blur_score: float
    face_count: int
    zone_breakdown: list[ZoneScoreOut]
    detections: list[dict] = []  # [{bbox: [cx,cy,w,h], confidence: float, zone: str}] in original image px space
    model_version: str
    created_at: datetime
    recommendations: list["RecommendationOut"] = []

    model_config = {"from_attributes": True}


class RecommendationOut(BaseModel):
    id: uuid.UUID
    category: str
    text: str
    priority: int

    model_config = {"from_attributes": True}


class SessionOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    image_id: uuid.UUID
    status: str
    created_at: datetime
    report: ReportOut | None = None
    recommendations: list[RecommendationOut] = []

    model_config = {"from_attributes": True}


class SessionListItem(BaseModel):
    id: uuid.UUID
    image_id: uuid.UUID
    status: str
    overall_score: float | None
    severity_level: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class HistoryResponse(BaseModel):
    items: list[SessionListItem]
    total: int
    page: int
    page_size: int
