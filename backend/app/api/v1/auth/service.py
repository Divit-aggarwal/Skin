import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth.repository import AuthRepository
from app.api.v1.auth.schemas import TokenResponse, UserOut
from app.exceptions import BadRequestError, ConflictError, UnauthorizedError
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = AuthRepository(db)

    async def register(self, email: str, password: str) -> TokenResponse:
        if await self.repo.get_by_email(email):
            raise ConflictError("Email already registered")
        user = await self.repo.create_user(email, hash_password(password))
        return await self._issue_tokens(user)

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedError("Invalid credentials")
        return await self._issue_tokens(user)

    async def refresh(self, refresh_token_str: str) -> TokenResponse:
        payload = decode_token(refresh_token_str)
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")

        jti = uuid.UUID(payload["jti"])
        stored = await self.repo.get_refresh_token_by_jti(jti)
        if not stored or stored.revoked_at is not None:
            raise UnauthorizedError("Token revoked or not found")

        if stored.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
            raise UnauthorizedError("Token expired")

        user = await self.repo.get_user_by_id(uuid.UUID(payload["sub"]))
        if not user:
            raise UnauthorizedError("User not found")

        await self.repo.revoke_refresh_token(jti)
        return await self._issue_tokens(user)

    async def logout(self, refresh_token_str: str, current_user_id: uuid.UUID) -> None:
        payload = decode_token(refresh_token_str)
        if payload.get("type") != "refresh":
            raise BadRequestError("Invalid token type")
        if uuid.UUID(payload["sub"]) != current_user_id:
            raise BadRequestError("Token does not belong to current user")
        await self.repo.revoke_refresh_token(uuid.UUID(payload["jti"]))

    async def _issue_tokens(self, user) -> TokenResponse:
        access_token = create_access_token(user.id, user.email)
        refresh_token_str, jti, expires_at = create_refresh_token(user.id)
        await self.repo.create_refresh_token(user.id, jti, expires_at)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token_str,
            user=UserOut.model_validate(user),
        )
