import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.image import Image


class ImageRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_image(
        self,
        user_id: uuid.UUID,
        mime_type: str,
        size_bytes: int,
        blur_score: float,
        face_count: int,
        quality_passed: bool,
        quality_reason: str | None,
    ) -> Image:
        image = Image(
            user_id=user_id,
            mime_type=mime_type,
            size_bytes=size_bytes,
            blur_score=blur_score,
            face_count=face_count,
            quality_passed=quality_passed,
            quality_reason=quality_reason,
        )
        self.db.add(image)
        await self.db.commit()
        await self.db.refresh(image)
        return image

    async def get_by_id(self, image_id: uuid.UUID) -> Image | None:
        result = await self.db.execute(
            select(Image).where(Image.id == image_id, Image.deleted_at.is_(None))
        )
        return result.scalar_one_or_none()

    async def get_by_user_id(self, user_id: uuid.UUID) -> list[Image]:
        result = await self.db.execute(
            select(Image).where(Image.user_id == user_id, Image.deleted_at.is_(None))
        )
        return list(result.scalars().all())
