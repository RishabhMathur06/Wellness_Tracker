import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_returns_reply_for_authenticated_user(
    client: AsyncClient, registered_user
):
    response = await client.post(
        "/api/v1/chat/message",
        headers=registered_user["headers"],
        json={"message": "I'm feeling a bit anxious today."},
    )
    assert response.status_code == 200
    data = response.json()
    assert "reply" in data
    assert len(data["reply"]) > 0
    assert data["pii_detected"] is False


@pytest.mark.asyncio
async def test_chat_redacts_credentials_and_flags_message(
    client: AsyncClient, registered_user
):
    response = await client.post(
        "/api/v1/chat/message",
        headers=registered_user["headers"],
        json={"message": "my password is SuperSecret99!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["pii_detected"] is True
    assert "credential" in data["pii_flags"]
    assert data["user_message_display"] is not None
    assert "SuperSecret99" not in data["user_message_display"]
    assert "[REDACTED:credential]" in data["user_message_display"]
    assert data["pii_notice"] is not None


@pytest.mark.asyncio
async def test_chat_rejects_unauthenticated_request(client: AsyncClient):
    response = await client.post(
        "/api/v1/chat/message",
        json={"message": "hello"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_chat_rejects_overly_long_message(client: AsyncClient, registered_user):
    response = await client.post(
        "/api/v1/chat/message",
        headers=registered_user["headers"],
        json={"message": "x" * 1001},
    )
    assert response.status_code == 422
