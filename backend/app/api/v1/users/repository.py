import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile
from app.models.refresh_token import RefreshToken
from app.models.user import User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(
            select(User).where(User.id == user_id, User.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_email_excluding(self, email: str, exclude_user_id: uuid.UUID) -> User | None:
        result = await self.db.execute(
            select(User).where(
                User.email == email,
                User.id != exclude_user_id,
                User.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def update_email(self, user_id: uuid.UUID, email: str) -> None:
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(email=email, updated_at=datetime.now(timezone.utc))
        )

    async def soft_delete(self, user_id: uuid.UUID) -> None:
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(deleted_at=datetime.now(timezone.utc))
        )

    async def revoke_all_refresh_tokens(self, user_id: uuid.UUID) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
            .values(revoked_at=datetime.now(timezone.utc))
        )


class ProfileRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_user_id(self, user_id: uuid.UUID) -> Profile | None:
        result = await self.db.execute(
            select(Profile).where(Profile.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def update_profile(self, user_id: uuid.UUID, fields: dict) -> None:
        fields["updated_at"] = datetime.now(timezone.utc)
        await self.db.execute(
            update(Profile).where(Profile.user_id == user_id).values(**fields)
        )
