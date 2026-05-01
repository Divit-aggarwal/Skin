import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.analysis.inference_client import call_inference
from app.api.v1.analysis.repository import AnalysisRepository
from app.api.v1.analysis.schemas import ReportOut, SessionOut
from app.api.v1.images.repository import ImageRepository
from app.exceptions import ForbiddenError, NotFoundError

_RECOMMENDATION_RULES = [
    {
        "category": "acne",
        "min_score": 67,
        "text": "Use a salicylic acid (2%) cleanser twice daily to target active breakouts.",
        "priority": 1,
    },
    {
        "category": "acne",
        "min_score": 33,
        "text": "Incorporate a niacinamide (10%) serum to reduce pore size and control sebum.",
        "priority": 2,
    },
    {
        "category": "wrinkle",
        "min_score": 67,
        "text": "Apply a retinol serum (0.25%) at night — increase concentration gradually over 8 weeks.",
        "priority": 1,
    },
    {
        "category": "wrinkle",
        "min_score": 33,
        "text": "Add a hyaluronic acid serum to your morning routine for hydration and visible plumping.",
        "priority": 2,
    },
    {
        "category": "oiliness",
        "min_score": 67,
        "text": "Use a kaolin clay mask once or twice a week to absorb excess sebum from the T-zone.",
        "priority": 1,
    },
    {
        "category": "oiliness",
        "min_score": 33,
        "text": "Switch to a water-based, oil-free moisturiser to balance hydration without clogging pores.",
        "priority": 2,
    },
]

_SPF_REC = {
    "category": "general",
    "text": "Apply SPF 30+ broad-spectrum sunscreen every morning — the single most evidence-backed anti-ageing step.",
    "priority": 10,
}


def _build_recommendations(acne: float, wrinkle: float, oiliness: float) -> list[dict]:
    scores = {"acne": acne, "wrinkle": wrinkle, "oiliness": oiliness}
    recs = [
        {"category": r["category"], "text": r["text"], "priority": r["priority"]}
        for r in _RECOMMENDATION_RULES
        if scores[r["category"]] >= r["min_score"]
    ]
    recs.append(_SPF_REC)
    return recs


class AnalysisService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = AnalysisRepository(db)
        self.image_repo = ImageRepository(db)

    async def create_session(
        self, user_id: uuid.UUID, image_id: uuid.UUID, image_data: str
    ) -> SessionOut:
        image = await self.image_repo.get_by_id(image_id)
        if image is None or image.user_id != user_id:
            raise NotFoundError("Image not found")

        session = await self.repo.create_session(user_id=user_id, image_id=image_id)

        infer_result = await call_inference(image_data=image_data, mime_type=image.mime_type)

        await self._finalize(session, infer_result)
        return await self.get_session(session.id, user_id)

    async def _finalize(self, session, infer_result: dict) -> None:
        await self.repo.create_report(
            session_id=session.id,
            acne_score=infer_result["acne_score"],
            wrinkle_score=infer_result["wrinkle_score"],
            oiliness_score=infer_result["oiliness_score"],
            overall_score=infer_result["overall_score"],
            severity_level=infer_result["severity_level"],
            blur_score=infer_result["blur_score"],
            face_count=infer_result["face_count"],
            zone_breakdown=infer_result["acne_zones"],
            yolo_detections=infer_result.get("yolo_detections", []),
            model_version=infer_result["model_version"],
        )
        recs = _build_recommendations(
            infer_result["acne_score"],
            infer_result["wrinkle_score"],
            infer_result["oiliness_score"],
        )
        await self.repo.create_recommendations(session.id, recs)
        await self.repo.update_session_status(session, "completed")
        await self.db.commit()

    async def get_session(self, session_id: uuid.UUID, user_id: uuid.UUID) -> SessionOut:
        session = await self.repo.get_session_by_id(session_id)
        if session is None:
            raise NotFoundError("Session not found")
        if session.user_id != user_id:
            raise ForbiddenError("Not your session")

        report = await self.repo.get_report_by_session(session_id)
        recommendations = await self.repo.get_recommendations_by_session(session_id)

        report_out = None
        if report:
            report_out = ReportOut(
                id=report.id,
                session_id=report.session_id,
                acne_score=report.acne_score,
                wrinkle_score=report.wrinkle_score,
                oiliness_score=report.oiliness_score,
                overall_score=report.overall_score,
                severity_level=report.severity_level,
                blur_score=report.blur_score,
                face_count=report.face_count,
                zone_breakdown=report.zone_breakdown,
                detections=report.yolo_detections,
                model_version=report.model_version,
                created_at=report.created_at,
                recommendations=[
                    {"id": r.id, "category": r.category, "text": r.text, "priority": r.priority}
                    for r in recommendations
                ],
            )

        return SessionOut(
            id=session.id,
            user_id=session.user_id,
            image_id=session.image_id,
            status=session.status,
            created_at=session.created_at,
            report=report_out,
            recommendations=[
                {"id": r.id, "category": r.category, "text": r.text, "priority": r.priority}
                for r in recommendations
            ],
        )

    async def get_history(self, user_id: uuid.UUID, page: int, page_size: int) -> dict:
        items, total = await self.repo.get_history(user_id, page, page_size)
        return {"items": items, "total": total, "page": page, "page_size": page_size}
