import pytest

from app.services.pii_service import PIIService
from app.services.email_service import EmailService


pii = PIIService()


def test_redacts_password_with_context():
    result = pii.scan_and_redact("my password is SuperSecret123!")
    assert result.pii_detected
    assert "credential" in result.flags
    assert "SuperSecret123" not in result.sanitized_text
    assert "[REDACTED:credential]" in result.sanitized_text


def test_redacts_credit_card():
    result = pii.scan_and_redact("I paid with 4532-1488-0343-6467")
    assert result.pii_detected
    assert "payment_card" in result.flags
    assert "4532" not in result.sanitized_text


def test_redacts_account_number_with_keyword():
    result = pii.scan_and_redact("my account number is 123456789012")
    assert result.pii_detected
    assert "123456789012" not in result.sanitized_text


def test_redacts_api_key():
    result = pii.scan_and_redact("here is my key sk-abcdefghijklmnopqrstuvwxyz123456")
    assert result.pii_detected
    assert "api_key" in result.flags


def test_leaves_normal_message_untouched():
    text = "I'm feeling stressed about my exam tomorrow."
    result = pii.scan_and_redact(text)
    assert not result.pii_detected
    assert result.sanitized_text == text


def test_leaves_short_numbers_untouched():
    result = pii.scan_and_redact("I slept for 6 hours and drank 2 coffees.")
    assert not result.pii_detected


def test_empty_string_returns_unchanged():
    result = pii.scan_and_redact("")
    assert not result.pii_detected
    assert result.sanitized_text == ""


def test_flag_label_returns_human_readable_text():
    assert pii.flag_label("credential") == "password or secret"
    assert pii.flag_label("payment_card") == "payment card"


@pytest.mark.asyncio
async def test_email_service_skips_when_not_configured():
    service = EmailService()
    assert service.is_configured is False
    sent = await service.send_email("guardian@test.com", "Subject", "Body")
    assert sent is False


@pytest.mark.asyncio
async def test_threshold_alert_not_sent_for_low_scores():
    service = EmailService()
    sent = await service.maybe_send_threshold_alert(
        guardian_email="guardian@test.com",
        user_name="Test",
        source="chat",
        stress=3.0,
        anxiety=2.0,
        evidence={"message": "I'm okay today."},
    )
    assert sent is False
