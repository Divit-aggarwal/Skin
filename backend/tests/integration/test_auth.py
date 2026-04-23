import pytest
from httpx import AsyncClient


REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
REFRESH_URL = "/api/v1/auth/refresh"
LOGOUT_URL = "/api/v1/auth/logout"

USER_EMAIL = "test@example.com"
USER_PASSWORD = "securepass123"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

async def register(client: AsyncClient, email: str = USER_EMAIL, password: str = USER_PASSWORD):
    return await client.post(REGISTER_URL, json={"email": email, "password": password})


async def login(client: AsyncClient, email: str = USER_EMAIL, password: str = USER_PASSWORD):
    return await client.post(LOGIN_URL, json={"email": email, "password": password})


def auth_headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    resp = await register(client)
    assert resp.status_code == 201
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    assert body["user"]["email"] == USER_EMAIL


@pytest.mark.asyncio
async def test_register_duplicate_email_409(client: AsyncClient):
    await register(client)
    resp = await register(client)
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "CONFLICT"


@pytest.mark.asyncio
async def test_register_weak_password_422(client: AsyncClient):
    resp = await client.post(REGISTER_URL, json={"email": USER_EMAIL, "password": "short"})
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await register(client)
    resp = await login(client)
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body


@pytest.mark.asyncio
async def test_login_wrong_password_401(client: AsyncClient):
    await register(client)
    resp = await client.post(LOGIN_URL, json={"email": USER_EMAIL, "password": "wrongpassword"})
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


# ---------------------------------------------------------------------------
# Refresh
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_refresh_success(client: AsyncClient):
    tokens = (await register(client)).json()
    resp = await client.post(REFRESH_URL, json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    body = resp.json()
    assert "access_token" in body
    assert "refresh_token" in body
    # Rotated — new refresh token must differ
    assert body["refresh_token"] != tokens["refresh_token"]


@pytest.mark.asyncio
async def test_refresh_revoked_token_401(client: AsyncClient):
    tokens = (await register(client)).json()
    refresh_token = tokens["refresh_token"]

    # Logout revokes the refresh token
    await client.post(
        LOGOUT_URL,
        json={"refresh_token": refresh_token},
        headers=auth_headers(tokens["access_token"]),
    )

    resp = await client.post(REFRESH_URL, json={"refresh_token": refresh_token})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient):
    tokens = (await register(client)).json()
    resp = await client.post(
        LOGOUT_URL,
        json={"refresh_token": tokens["refresh_token"]},
        headers=auth_headers(tokens["access_token"]),
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_logout_wrong_owner_400(client: AsyncClient):
    # Register two users and try to revoke user A's token while authenticated as user B
    tokens_a = (await register(client, email="a@example.com")).json()
    tokens_b = (await register(client, email="b@example.com")).json()

    resp = await client.post(
        LOGOUT_URL,
        json={"refresh_token": tokens_a["refresh_token"]},
        headers=auth_headers(tokens_b["access_token"]),
    )
    assert resp.status_code == 400


# ---------------------------------------------------------------------------
# get_current_user (exercised via the logout endpoint)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_current_user_valid(client: AsyncClient):
    tokens = (await register(client)).json()
    resp = await client.post(
        LOGOUT_URL,
        json={"refresh_token": tokens["refresh_token"]},
        headers=auth_headers(tokens["access_token"]),
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_get_current_user_missing_token_401(client: AsyncClient):
    resp = await client.post(LOGOUT_URL, json={"refresh_token": "anything"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user_expired_token_401(client: AsyncClient):
    import time
    from jose import jwt
    from app.config import settings

    tokens = (await register(client)).json()
    # Craft a token that's already expired
    import uuid
    from datetime import datetime, timezone, timedelta
    payload = {
        "sub": str(uuid.uuid4()),
        "email": USER_EMAIL,
        "type": "access",
        "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
    }
    expired_token = jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    resp = await client.post(
        LOGOUT_URL,
        json={"refresh_token": tokens["refresh_token"]},
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp.status_code == 401
