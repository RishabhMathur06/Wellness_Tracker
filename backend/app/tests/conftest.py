"""
Shared pytest fixtures for API and service tests.
Uses an in-memory SQLite database and mocks external AI/email services.
"""
import os

# Set test env before app modules load settings-dependent clients
os.environ.setdefault("GEMINI_API_KEY", "dummy_key_if_not_set")
os.environ.setdefault("GMAIL_ADDRESS", "")
os.environ.setdefault("GMAIL_APP_PASSWORD", "")
os.environ.setdefault("SECRET_KEY", "test-secret-key-for-pytest-only")

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.core.database import Base, get_db
from app.models.user import User  # noqa: F401 — register ORM models
from app.models.metric import Metric  # noqa: F401

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def client(db_engine):
    session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def registered_user(client):
    """Register a user and return auth headers + user payload."""
    payload = {
        "email": "student@example.com",
        "password": "securepass123",
        "full_name": "Test Student",
        "guardian_email": "guardian@example.com",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    return {
        "headers": {"Authorization": f"Bearer {data['access_token']}"},
        "user": data["user"],
        "credentials": {"email": payload["email"], "password": payload["password"]},
    }


@pytest.fixture(autouse=True)
def mock_external_services(monkeypatch):
    """Avoid real Gemini and SMTP calls during tests."""

    async def mock_chat(message, history):
        return "Thank you for sharing. How can I support you today?"

    async def mock_scores(message):
        return {"stress": 4.0, "anxiety": 3.0}

    async def mock_analyze(image_data):
        return {
            "stress_score": 5.0,
            "anxiety_score": 4.0,
            "detected_emotions": ["calm"],
            "analysis": "Mock analysis.",
            "recommendation": "Mock recommendation.",
        }

    async def mock_send_email(self, to, subject, body):
        return False

    async def mock_weekly_report(self, guardian_email, user_name, report_data):
        return False

    async def mock_threshold_alert(self, **kwargs):
        return False

    monkeypatch.setattr(
        "app.api.v1.endpoints.chat.gemini_service.chat_therapeutic", mock_chat
    )
    monkeypatch.setattr(
        "app.api.v1.endpoints.chat.gemini_service.extract_scores_from_chat", mock_scores
    )
    monkeypatch.setattr(
        "app.api.v1.endpoints.tracker.gemini_service.analyze_emotion_multimodal",
        mock_analyze,
    )
    monkeypatch.setattr(
        "app.services.email_service.EmailService.send_email", mock_send_email
    )
    monkeypatch.setattr(
        "app.services.email_service.EmailService.send_weekly_report", mock_weekly_report
    )
    monkeypatch.setattr(
        "app.services.email_service.EmailService.maybe_send_threshold_alert",
        mock_threshold_alert,
    )
