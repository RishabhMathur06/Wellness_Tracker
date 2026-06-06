import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_creates_user_and_returns_token(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@test.com",
            "password": "password123",
            "full_name": "New User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "newuser@test.com"
    assert data["user"]["full_name"] == "New User"


@pytest.mark.asyncio
async def test_register_rejects_duplicate_email(client: AsyncClient, registered_user):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": registered_user["credentials"]["email"],
            "password": "password123",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_rejects_short_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "shortpw@test.com", "password": "abc"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_with_valid_credentials(client: AsyncClient, registered_user):
    response = await client.post(
        "/api/v1/auth/login",
        json=registered_user["credentials"],
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_rejects_wrong_password(client: AsyncClient, registered_user):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": registered_user["credentials"]["email"],
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_returns_current_user(client: AsyncClient, registered_user):
    response = await client.get(
        "/api/v1/auth/me",
        headers=registered_user["headers"],
    )
    assert response.status_code == 200
    assert response.json()["email"] == registered_user["user"]["email"]


@pytest.mark.asyncio
async def test_me_requires_authentication(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
