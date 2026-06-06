import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_metrics_requires_authentication(client: AsyncClient):
    response = await client.get("/api/v1/tracker/metrics")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_metrics_returns_seven_days(client: AsyncClient, registered_user):
    response = await client.get(
        "/api/v1/tracker/metrics",
        headers=registered_user["headers"],
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 7
    for day in data:
        assert "day" in day
        assert "stress" in day
        assert "anxiety" in day
        assert 0 <= day["stress"] <= 10
        assert 0 <= day["anxiety"] <= 10


@pytest.mark.asyncio
async def test_reports_requires_authentication(client: AsyncClient):
    response = await client.get("/api/v1/tracker/reports")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_reports_returns_summary_fields(client: AsyncClient, registered_user):
    response = await client.get(
        "/api/v1/tracker/reports",
        headers=registered_user["headers"],
    )
    assert response.status_code == 200
    data = response.json()
    assert "avg_stress" in data
    assert "avg_anxiety" in data
    assert "summary" in data
    assert "email_sent" in data
    assert isinstance(data["email_sent"], bool)


@pytest.mark.asyncio
async def test_analyze_emotion_rejects_non_image(client: AsyncClient, registered_user):
    response = await client.post(
        "/api/v1/tracker/analyze-emotion",
        headers=registered_user["headers"],
        files={"file": ("notes.txt", b"not an image", "text/plain")},
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_analyze_emotion_accepts_image(client: AsyncClient, registered_user):
    # Minimal valid JPEG header bytes for upload test
    fake_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 100
    response = await client.post(
        "/api/v1/tracker/analyze-emotion",
        headers=registered_user["headers"],
        files={"file": ("photo.jpg", fake_jpeg, "image/jpeg")},
    )
    assert response.status_code == 200
    data = response.json()
    assert "stress_score" in data
    assert "anxiety_score" in data
    assert 0 <= data["stress_score"] <= 10
    assert 0 <= data["anxiety_score"] <= 10
