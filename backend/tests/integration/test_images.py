import base64
from unittest.mock import patch

import cv2
import numpy as np
import pytest
from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
UPLOAD_URL = "/api/v1/images/upload"

USER_EMAIL = "imguser@example.com"
USER_PASSWORD = "securepass123"

_QG_PATH = "app.api.v1.images.service.validate_image"

_QG_PASS = {"passed": True, "blur_score": 250.0, "face_count": 1}
_QG_BLURRY = {"passed": False, "blur_score": 12.0, "face_count": 0, "reason": "Image is too blurry"}
_QG_NO_FACE = {"passed": False, "blur_score": 250.0, "face_count": 0, "reason": "No face detected"}
_QG_MULTI = {"passed": False, "blur_score": 250.0, "face_count": 2, "reason": "Multiple faces detected"}


def _small_jpeg_b64() -> str:
    """Return base64-encoded minimal valid JPEG (50x50 white image)."""
    img = np.ones((50, 50, 3), dtype=np.uint8) * 200
    _, buf = cv2.imencode(".jpg", img)
    return base64.b64encode(buf.tobytes()).decode()


def _oversized_b64() -> str:
    """Return base64-encoded bytes that exceed 3 MB."""
    return base64.b64encode(b"\x00" * (3 * 1024 * 1024 + 1)).decode()


async def _register_and_token(client: AsyncClient) -> str:
    resp = await client.post(REGISTER_URL, json={"email": USER_EMAIL, "password": USER_PASSWORD})
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Success
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upload_success(client: AsyncClient):
    token = await _register_and_token(client)
    with patch(_QG_PATH, return_value=_QG_PASS):
        resp = await client.post(
            UPLOAD_URL,
            json={"image_data": _small_jpeg_b64(), "mime_type": "image/jpeg"},
            headers=_auth(token),
        )
    assert resp.status_code == 201
    body = resp.json()
    assert body["quality_passed"] is True
    assert body["face_count"] == 1
    assert "id" in body


# ---------------------------------------------------------------------------
# Auth guard
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upload_unauthenticated_401(client: AsyncClient):
    resp = await client.post(
        UPLOAD_URL,
        json={"image_data": _small_jpeg_b64(), "mime_type": "image/jpeg"},
    )
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Size
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upload_too_large_413(client: AsyncClient):
    token = await _register_and_token(client)
    resp = await client.post(
        UPLOAD_URL,
        json={"image_data": _oversized_b64(), "mime_type": "image/jpeg"},
        headers=_auth(token),
    )
    assert resp.status_code == 413
    assert resp.json()["error"]["code"] == "IMAGE_TOO_LARGE"


# ---------------------------------------------------------------------------
# MIME type
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upload_invalid_mime_422(client: AsyncClient):
    token = await _register_and_token(client)
    resp = await client.post(
        UPLOAD_URL,
        json={"image_data": _small_jpeg_b64(), "mime_type": "image/gif"},
        headers=_auth(token),
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "INVALID_MIME"


# ---------------------------------------------------------------------------
# Malformed base64
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upload_malformed_base64_422(client: AsyncClient):
    token = await _register_and_token(client)
    resp = await client.post(
        UPLOAD_URL,
        json={"image_data": "not-valid-base64!!!", "mime_type": "image/jpeg"},
        headers=_auth(token),
    )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "MALFORMED_BASE64"


# ---------------------------------------------------------------------------
# Quality gate rejections
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_upload_blurry_422(client: AsyncClient):
    token = await _register_and_token(client)
    with patch(_QG_PATH, return_value=_QG_BLURRY):
        resp = await client.post(
            UPLOAD_URL,
            json={"image_data": _small_jpeg_b64(), "mime_type": "image/jpeg"},
            headers=_auth(token),
        )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "IMAGE_QUALITY_FAILED"
    assert "blurry" in resp.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_upload_no_face_422(client: AsyncClient):
    token = await _register_and_token(client)
    with patch(_QG_PATH, return_value=_QG_NO_FACE):
        resp = await client.post(
            UPLOAD_URL,
            json={"image_data": _small_jpeg_b64(), "mime_type": "image/jpeg"},
            headers=_auth(token),
        )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "IMAGE_QUALITY_FAILED"
    assert "face" in resp.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_upload_multiple_faces_422(client: AsyncClient):
    token = await _register_and_token(client)
    with patch(_QG_PATH, return_value=_QG_MULTI):
        resp = await client.post(
            UPLOAD_URL,
            json={"image_data": _small_jpeg_b64(), "mime_type": "image/jpeg"},
            headers=_auth(token),
        )
    assert resp.status_code == 422
    assert resp.json()["error"]["code"] == "IMAGE_QUALITY_FAILED"
    assert "multiple" in resp.json()["error"]["message"].lower()
