from pydantic import BaseModel


class InferRequest(BaseModel):
    image_data: str  # base64-encoded image
    mime_type: str


class ZoneScore(BaseModel):
    zone: str
    score: float


class InferResponse(BaseModel):
    acne_score: float
    wrinkle_score: float
    oiliness_score: float
    overall_score: float
    severity_level: str       # "mild" | "moderate" | "severe"
    acne_zones: list[ZoneScore]
    blur_score: float
    face_count: int
    model_version: str
