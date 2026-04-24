import base64
import uuid

import cv2
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.images.repository import ImageRepository
from app.api.v1.images.schemas import ImageOut
from app.exceptions import ImageQualityError, ImageTooLargeError, InvalidMimeTypeError, MalformedBase64Error
from app.utils.quality_gate import validate_image

_ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp"}
_MAX_SIZE_BYTES = 3 * 1024 * 1024  # 3 MB


class ImageService:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.repo = ImageRepository(db)

    async def upload(self, user_id: uuid.UUID, image_data: str, mime_type: str) -> ImageOut:
        if mime_type not in _ALLOWED_MIME_TYPES:
            raise InvalidMimeTypeError()

        # Strip optional data-URI prefix (e.g. "data:image/jpeg;base64,...")
        if "," in image_data:
            image_data = image_data.split(",", 1)[1]

        try:
            raw = base64.b64decode(image_data, validate=True)
        except Exception:
            raise MalformedBase64Error()

        if len(raw) > _MAX_SIZE_BYTES:
            raise ImageTooLargeError()

        arr = np.frombuffer(raw, dtype=np.uint8)
        bgr = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if bgr is None:
            raise MalformedBase64Error()

        image_array = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)

        result = validate_image(image_array)

        if not result["passed"]:
            raise ImageQualityError(result["reason"])

        image = await self.repo.create_image(
            user_id=user_id,
            mime_type=mime_type,
            size_bytes=len(raw),
            blur_score=result["blur_score"],
            face_count=result["face_count"],
            quality_passed=True,
            quality_reason=None,
        )
        return ImageOut.model_validate(image)
