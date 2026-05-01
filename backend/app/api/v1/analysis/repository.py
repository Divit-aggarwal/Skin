import uuid

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis_report import AnalysisReport
from app.models.analysis_session import AnalysisSession
from app.models.recommendation import Recommendation


class AnalysisRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_session(self, user_id: uuid.UUID, image_id: uuid.UUID) -> AnalysisSession:
        session = AnalysisSession(user_id=user_id, image_id=image_id, status="pending")
        self.db.add(session)
        await self.db.flush()
        return session

    async def update_session_status(self, session: AnalysisSession, status: str) -> None:
        session.status = status
        await self.db.flush()

    async def create_report(
        self,
        session_id: uuid.UUID,
        acne_score: float,
        wrinkle_score: float,
        oiliness_score: float,
        overall_score: float,
        severity_level: str,
        blur_score: float,
        face_count: int,
        zone_breakdown: list,
        yolo_detections: list,
        model_version: str,
    ) -> AnalysisReport:
        report = AnalysisReport(
            session_id=session_id,
            acne_score=acne_score,
            wrinkle_score=wrinkle_score,
            oiliness_score=oiliness_score,
            overall_score=overall_score,
            severity_level=severity_level,
            blur_score=blur_score,
            face_count=face_count,
            zone_breakdown=zone_breakdown,
            yolo_detections=yolo_detections,
            model_version=model_version,
        )
        self.db.add(report)
        await self.db.flush()
        return report

    async def create_recommendations(
        self, session_id: uuid.UUID, items: list[dict]
    ) -> list[Recommendation]:
        recs = [Recommendation(session_id=session_id, **item) for item in items]
        self.db.add_all(recs)
        await self.db.flush()
        return recs

    async def get_session_by_id(self, session_id: uuid.UUID) -> AnalysisSession | None:
        result = await self.db.execute(
            select(AnalysisSession).where(
                AnalysisSession.id == session_id,
                AnalysisSession.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def get_report_by_session(self, session_id: uuid.UUID) -> AnalysisReport | None:
        result = await self.db.execute(
            select(AnalysisReport).where(AnalysisReport.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def get_recommendations_by_session(self, session_id: uuid.UUID) -> list[Recommendation]:
        result = await self.db.execute(
            select(Recommendation)
            .where(Recommendation.session_id == session_id)
            .order_by(Recommendation.priority)
        )
        return list(result.scalars().all())

    async def get_history(
        self, user_id: uuid.UUID, page: int, page_size: int
    ) -> tuple[list[dict], int]:
        base_q = select(AnalysisSession).where(
            AnalysisSession.user_id == user_id,
            AnalysisSession.deleted_at.is_(None),
        )
        count_result = await self.db.execute(
            select(func.count()).select_from(base_q.subquery())
        )
        total = count_result.scalar_one()

        sessions_result = await self.db.execute(
            base_q.order_by(desc(AnalysisSession.created_at))
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        sessions = list(sessions_result.scalars().all())

        items = []
        for s in sessions:
            report = await self.get_report_by_session(s.id)
            items.append({
                "id": s.id,
                "image_id": s.image_id,
                "status": s.status,
                "overall_score": report.overall_score if report else None,
                "severity_level": report.severity_level if report else None,
                "created_at": s.created_at,
            })
        return items, total
