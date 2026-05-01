import base64
import uuid
from unittest.mock import AsyncMock, patch

import cv2
import numpy as np
import pytest
from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
UPLOAD_URL = "/api/v1/images/upload"
SESSIONS_URL = "/api/v1/analysis/sessions"
HISTORY_URL = "/api/v1/analysis/history"

USER_EMAIL = "analysis_user@example.com"
USER_PASSWORD = "testpassword123"

_QG_PATH = "app.api.v1.images.service.validate_image"
_INFER_PATH = "app.api.v1.analysis.service.call_inference"

_QG_PASS = {"passed": True, "blur_score": 250.0, "face_count": 1}

_INFER_RESULT = {
    "acne_score": 45.0,
    "wrinkle_score": 20.0,
    "oiliness_score": 55.0,
    "overall_score": 38.5,
    "severity_level": "moderate",
    "acne_zones": [
        {"zone": "forehead", "score": 30.0},
        {"zone": "nose", "score": 15.0},
        {"zone": "left_cheek", "score": 45.0},
        {"zone": "right_cheek", "score": 10.0},
        {"zone": "chin", "score": 5.0},
    ],
    "blur_score": 250.0,
    "face_count": 1,
    "model_version": "yolo11n-acne-v0.1_unet-wrinkle-v0.1_oiliness-heuristic-v1",
    "yolo_detections": [],
}


def _small_jpeg_b64() -> str:
    img = np.ones((50, 50, 3), dtype=np.uint8) * 200
    _, buf = cv2.imencode(".jpg", img)
    return base64.b64encode(buf.tobytes()).decode()


async def _register_and_token(client: AsyncClient, email: str = USER_EMAIL) -> str:
    resp = await client.post(REGISTER_URL, json={"email": email, "password": USER_PASSWORD})
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


async def _upload_image(client: AsyncClient, token: str) -> str:
    with patch(_QG_PATH, return_value=_QG_PASS):
        resp = await client.post(
            UPLOAD_URL,
            json={"image_data": _small_jpeg_b64(), "mime_type": "image/jpeg"},
            headers=_auth(token),
        )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


# ---------------------------------------------------------------------------
# Success cases
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_session_success(client: AsyncClient):
    token = await _register_and_token(client)
    image_id = await _upload_image(client, token)

    with patch(_INFER_PATH, new=AsyncMock(return_value=_INFER_RESULT)):
        resp = await client.post(
            SESSIONS_URL,
            json={"image_id": image_id, "image_data": _small_jpeg_b64()},
            headers=_auth(token),
        )

    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "completed"
    assert "report" in body
    report = body["report"]
    assert 0.0 <= report["acne_score"] <= 100.0
    assert 0.0 <= report["wrinkle_score"] <= 100.0
    assert 0.0 <= report["oiliness_score"] <= 100.0
    assert 0.0 <= report["overall_score"] <= 100.0
    assert report["severity_level"] in ("mild", "moderate", "severe")
    assert report["model_version"] == "yolo11n-acne-v0.1_unet-wrinkle-v0.1_oiliness-heuristic-v1"
    assert len(body["recommendations"]) >= 1


@pytest.mark.asyncio
async def test_get_session_success(client: AsyncClient):
    token = await _register_and_token(client)
    image_id = await _upload_image(client, token)

    with patch(_INFER_PATH, new=AsyncMock(return_value=_INFER_RESULT)):
        create_resp = await client.post(
            SESSIONS_URL,
            json={"image_id": image_id, "image_data": _small_jpeg_b64()},
            headers=_auth(token),
        )
    session_id = create_resp.json()["id"]

    resp = await client.get(f"{SESSIONS_URL}/{session_id}", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["id"] == session_id


@pytest.mark.asyncio
async def test_get_report_success(client: AsyncClient):
    token = await _register_and_token(client)
    image_id = await _upload_image(client, token)

    with patch(_INFER_PATH, new=AsyncMock(return_value=_INFER_RESULT)):
        create_resp = await client.post(
            SESSIONS_URL,
            json={"image_id": image_id, "image_data": _small_jpeg_b64()},
            headers=_auth(token),
        )
    session_id = create_resp.json()["id"]

    resp = await client.get(f"{SESSIONS_URL}/{session_id}/report", headers=_auth(token))
    assert resp.status_code == 200
    assert resp.json()["session_id"] == session_id


# ---------------------------------------------------------------------------
# Error cases
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_create_session_image_not_found(client: AsyncClient):
    token = await _register_and_token(client)
    resp = await client.post(
        SESSIONS_URL,
        json={"image_id": str(uuid.uuid4()), "image_data": _small_jpeg_b64()},
        headers=_auth(token),
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_create_session_image_not_owned(client: AsyncClient):
    token_a = await _register_and_token(client, "user_a@example.com")
    token_b = await _register_and_token(client, "user_b@example.com")

    image_id = await _upload_image(client, token_a)

    resp = await client.post(
        SESSIONS_URL,
        json={"image_id": image_id, "image_data": _small_jpeg_b64()},
        headers=_auth(token_b),
    )
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_get_session_not_owned(client: AsyncClient):
    token_a = await _register_and_token(client, "owner_a@example.com")
    token_b = await _register_and_token(client, "owner_b@example.com")

    image_id = await _upload_image(client, token_a)
    with patch(_INFER_PATH, new=AsyncMock(return_value=_INFER_RESULT)):
        create_resp = await client.post(
            SESSIONS_URL,
            json={"image_id": image_id, "image_data": _small_jpeg_b64()},
            headers=_auth(token_a),
        )
    session_id = create_resp.json()["id"]

    resp = await client.get(f"{SESSIONS_URL}/{session_id}", headers=_auth(token_b))
    assert resp.status_code == 403


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_history_empty_for_new_user(client: AsyncClient):
    token = await _register_and_token(client, "history_new@example.com")
    resp = await client.get(HISTORY_URL, headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["items"] == []
    assert body["total"] == 0


@pytest.mark.asyncio
async def test_history_pagination(client: AsyncClient):
    token = await _register_and_token(client, "history_page@example.com")

    for _ in range(3):
        image_id = await _upload_image(client, token)
        with patch(_INFER_PATH, new=AsyncMock(return_value=_INFER_RESULT)):
            await client.post(
                SESSIONS_URL,
                json={"image_id": image_id, "image_data": _small_jpeg_b64()},
                headers=_auth(token),
            )

    resp = await client.get(f"{HISTORY_URL}?page=1&page_size=2", headers=_auth(token))
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 3
    assert len(body["items"]) == 2

    resp2 = await client.get(f"{HISTORY_URL}?page=2&page_size=2", headers=_auth(token))
    assert resp2.json()["items"].__len__() == 1
