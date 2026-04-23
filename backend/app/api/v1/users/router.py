from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.users.schemas import (
    DeleteAccountRequest,
    ProfileOut,
    UpdateProfileRequest,
    UpdateUserRequest,
    UserOut,
)
from app.api.v1.users.service import ProfileService, UserService
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserService(None).get_me(current_user)


@router.put("/me", response_model=UserOut)
async def update_me(
    body: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.email is None:
        return UserOut.model_validate(current_user)
    return await UserService(db).update_email(current_user, body.email)


@router.get("/me/profile", response_model=ProfileOut)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ProfileService(db).get_profile(current_user.id)


@router.put("/me/profile", response_model=ProfileOut)
async def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await ProfileService(db).update_profile(current_user.id, body)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    body: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await UserService(db).delete_account(current_user, body.password)
