import httpx
from loguru import logger

from app.config import settings
from app.exceptions import InferenceServiceError


async def call_inference(image_data: str, mime_type: str) -> dict:
    """Call inference service /infer endpoint.

    Returns the parsed JSON response dict on success.
    Raises InferenceServiceError on timeout or connection failure.
    """
    payload = {"image_data": image_data, "mime_type": mime_type}
    try:
        async with httpx.AsyncClient(timeout=settings.inference_timeout_seconds) as client:
            response = await client.post(f"{settings.inference_url}/infer", json=payload)
        response.raise_for_status()
        return response.json()
    except httpx.TimeoutException:
        logger.error("Inference service timed out after {}s", settings.inference_timeout_seconds)
        raise InferenceServiceError("Inference service timed out")
    except httpx.ConnectError:
        logger.error("Could not connect to inference service at {}", settings.inference_url)
        raise InferenceServiceError("Inference service unreachable")
    except httpx.HTTPStatusError as e:
        logger.error("Inference service returned {}: {}", e.response.status_code, e.response.text)
        raise InferenceServiceError(f"Inference service error: {e.response.status_code}")
