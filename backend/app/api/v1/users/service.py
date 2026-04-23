import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.users.repository import ProfileRepository, UserRepository
from app.api.v1.users.schemas import ProfileOut, UpdateProfileRequest, UserOut
from app.exceptions import ConflictError, NotFoundError, UnauthorizedError
from app.models.user import User
from app.utils.security import verify_password


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    def get_me(self, user: User) -> UserOut:
        return UserOut.model_validate(user)

    async def update_email(self, user: User, new_email: str) -> UserOut:
        if await self.repo.get_by_email_excluding(new_email, user.id):
            raise ConflictError("Email already in use")
        await self.repo.update_email(user.id, new_email)
        user.email = new_email
        return UserOut.model_validate(user)

    async def delete_account(self, user: User, password: str) -> None:
        if not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid password")
        await self.repo.revoke_all_refresh_tokens(user.id)
        await self.repo.soft_delete(user.id)


class ProfileService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = ProfileRepository(db)

    async def get_profile(self, user_id: uuid.UUID) -> ProfileOut:
        profile = await self.repo.get_by_user_id(user_id)
        if not profile:
            raise NotFoundError("Profile not found")
        return ProfileOut.model_validate(profile)

    async def update_profile(self, user_id: uuid.UUID, body: UpdateProfileRequest) -> ProfileOut:
        fields = body.model_dump(exclude_unset=True)
        if fields:
            await self.repo.update_profile(user_id, fields)
        profile = await self.repo.get_by_user_id(user_id)
        if not profile:
            raise NotFoundError("Profile not found")
        return ProfileOut.model_validate(profile)
