from fastapi import status


class AppError(Exception):
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal server error"
    code: str = "INTERNAL_ERROR"

    def __init__(self, detail: str | None = None):
        self.detail = detail or self.__class__.detail
        super().__init__(self.detail)


class NotFoundError(AppError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"
    code = "NOT_FOUND"


class UnauthorizedError(AppError):
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Not authenticated"
    code = "UNAUTHORIZED"


class ForbiddenError(AppError):
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Permission denied"
    code = "FORBIDDEN"


class ConflictError(AppError):
    status_code = status.HTTP_409_CONFLICT
    detail = "Resource already exists"
    code = "CONFLICT"


class BadRequestError(AppError):
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Bad request"
    code = "BAD_REQUEST"


class ValidationError(AppError):
    status_code = 422
    detail = "Validation error"
    code = "VALIDATION_ERROR"


class ImageTooLargeError(AppError):
    status_code = 413
    detail = "Image exceeds the maximum allowed size of 3MB"
    code = "IMAGE_TOO_LARGE"


class InvalidMimeTypeError(AppError):
    status_code = 422
    detail = "Invalid MIME type. Allowed: image/jpeg, image/png, image/webp"
    code = "INVALID_MIME"


class ImageQualityError(AppError):
    status_code = 422
    code = "IMAGE_QUALITY_FAILED"


class MalformedBase64Error(AppError):
    status_code = 422
    detail = "Invalid or malformed base64 image data"
    code = "MALFORMED_BASE64"
