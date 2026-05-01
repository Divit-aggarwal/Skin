import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.analysis.schemas import (
    HistoryResponse,
    ReportOut,
    SessionCreateRequest,
    SessionOut,
)
from app.api.v1.analysis.service import AnalysisService
from app.dependencies import get_current_user, get_db
from app.models.user import User

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/sessions", response_model=SessionOut, status_code=201)
async def create_session(
    body: SessionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AnalysisService(db)
    return await svc.create_session(
        user_id=current_user.id,
        image_id=body.image_id,
        image_data=body.image_data,
    )


@router.get("/sessions/{session_id}", response_model=SessionOut)
async def get_session(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AnalysisService(db)
    return await svc.get_session(session_id=session_id, user_id=current_user.id)


@router.get("/sessions/{session_id}/report", response_model=ReportOut)
async def get_report(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AnalysisService(db)
    session = await svc.get_session(session_id=session_id, user_id=current_user.id)
    if session.report is None:
        from app.exceptions import NotFoundError
        raise NotFoundError("Report not yet available")
    return session.report


@router.get("/history", response_model=HistoryResponse)
async def get_history(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AnalysisService(db)
    return await svc.get_history(user_id=current_user.id, page=page, page_size=page_size)
