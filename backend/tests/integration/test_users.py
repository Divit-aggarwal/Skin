import pytest
from httpx import AsyncClient

REGISTER_URL = "/api/v1/auth/register"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/users/me"
PROFILE_URL = "/api/v1/users/me/profile"

USER_EMAIL = "user@example.com"
USER_PASSWORD = "securepass123"


async def register(client: AsyncClient, email: str = USER_EMAIL, password: str = USER_PASSWORD):
    return await client.post(REGISTER_URL, json={"email": email, "password": password})


def auth_headers(access_token: str) -> dict:
    return {"Authorization": f"Bearer {access_token}"}


# ---------------------------------------------------------------------------
# GET /users/me
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_me_authenticated(client: AsyncClient):
    tokens = (await register(client)).json()
    resp = await client.get(ME_URL, headers=auth_headers(tokens["access_token"]))
    assert resp.status_code == 200
    assert resp.json()["email"] == USER_EMAIL


@pytest.mark.asyncio
async def test_get_me_unauthenticated_401(client: AsyncClient):
    resp = await client.get(ME_URL)
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# PUT /users/me
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_email_success(client: AsyncClient):
    tokens = (await register(client)).json()
    resp = await client.put(
        ME_URL,
        json={"email": "new@example.com"},
        headers=auth_headers(tokens["access_token"]),
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "new@example.com"


@pytest.mark.asyncio
async def test_update_email_duplicate_409(client: AsyncClient):
    tokens_a = (await register(client, email="a@example.com")).json()
    await register(client, email="b@example.com")

    resp = await client.put(
        ME_URL,
        json={"email": "b@example.com"},
        headers=auth_headers(tokens_a["access_token"]),
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "CONFLICT"


# ---------------------------------------------------------------------------
# GET /users/me/profile
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_get_profile(client: AsyncClient):
    tokens = (await register(client)).json()
    resp = await client.get(PROFILE_URL, headers=auth_headers(tokens["access_token"]))
    assert resp.status_code == 200
    body = resp.json()
    assert "id" in body
    assert body["display_name"] is None
    assert body["skin_type"] is None


# ---------------------------------------------------------------------------
# PUT /users/me/profile
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient):
    tokens = (await register(client)).json()
    resp = await client.put(
        PROFILE_URL,
        json={"display_name": "Alice", "age": 28, "skin_type": "oily"},
        headers=auth_headers(tokens["access_token"]),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["display_name"] == "Alice"
    assert body["age"] == 28
    assert body["skin_type"] == "oily"


@pytest.mark.asyncio
async def test_update_profile_age_out_of_range_422(client: AsyncClient):
    tokens = (await register(client)).json()
    resp = await client.put(
        PROFILE_URL,
        json={"age": 0},
        headers=auth_headers(tokens["access_token"]),
    )
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# DELETE /users/me
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_delete_account_correct_password(client: AsyncClient):
    tokens = (await register(client)).json()
    resp = await client.request(
        "DELETE",
        ME_URL,
        json={"password": USER_PASSWORD},
        headers=auth_headers(tokens["access_token"]),
    )
    assert resp.status_code == 204


@pytest.mark.asyncio
async def test_delete_account_wrong_password_401(client: AsyncClient):
    tokens = (await register(client)).json()
    resp = await client.request(
        "DELETE",
        ME_URL,
        json={"password": "wrongpassword"},
        headers=auth_headers(tokens["access_token"]),
    )
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_deleted_user_cannot_login(client: AsyncClient):
    tokens = (await register(client)).json()
    await client.request(
        "DELETE",
        ME_URL,
        json={"password": USER_PASSWORD},
        headers=auth_headers(tokens["access_token"]),
    )
    resp = await client.post(LOGIN_URL, json={"email": USER_EMAIL, "password": USER_PASSWORD})
    assert resp.status_code == 401
