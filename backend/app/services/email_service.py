import asyncio
import logging
import smtplib
from email.mime.text import MIMEText
from typing import Any, Dict, Optional

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self):
        settings = get_settings()
        self.gmail_address = settings.GMAIL_ADDRESS
        self.gmail_app_password = settings.GMAIL_APP_PASSWORD
        self.stress_threshold = settings.STRESS_ALERT_THRESHOLD
        self.anxiety_threshold = settings.ANXIETY_ALERT_THRESHOLD

    @property
    def is_configured(self) -> bool:
        return bool(self.gmail_address and self.gmail_app_password)

    def _send_email_sync(self, to: str, subject: str, body: str) -> bool:
        msg = MIMEText(body, "plain")
        msg["From"] = self.gmail_address
        msg["To"] = to
        msg["Subject"] = subject

        with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
            server.starttls()
            server.login(self.gmail_address, self.gmail_app_password)
            server.sendmail(self.gmail_address, to, msg.as_string())
        return True

    async def send_email(self, to: str, subject: str, body: str) -> bool:
        if not to:
            logger.warning("No guardian email on file — skipping email.")
            return False
        if not self.is_configured:
            logger.warning(
                "Gmail not configured (set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in .env) — skipping email to %s",
                to,
            )
            return False
        try:
            await asyncio.to_thread(self._send_email_sync, to, subject, body)
            logger.info("Email sent to %s: %s", to, subject)
            return True
        except Exception as e:
            logger.error("Failed to send email to %s: %s", to, e)
            return False

    async def send_weekly_report(
        self,
        guardian_email: str,
        user_name: str,
        report_data: dict,
    ) -> bool:
        subject = f"Weekly Wellness Report for {user_name}"
        body = f"""Hello,

Here is the weekly wellness summary for {user_name}:

Average Stress:  {report_data.get('avg_stress', 'N/A')}/10
Average Anxiety: {report_data.get('avg_anxiety', 'N/A')}/10

AI Insight:
{report_data.get('summary', 'No summary available.')}

---
This report was generated automatically by Wellness Tracker.
"""
        return await self.send_email(guardian_email, subject, body)

    async def maybe_send_threshold_alert(
        self,
        guardian_email: Optional[str],
        user_name: str,
        source: str,
        stress: float,
        anxiety: float,
        evidence: Dict[str, Any],
    ) -> bool:
        stress_high = stress >= self.stress_threshold
        anxiety_high = anxiety >= self.anxiety_threshold
        if not stress_high and not anxiety_high:
            return False

        triggers = []
        if stress_high:
            triggers.append(f"Stress {stress}/10 (threshold: {self.stress_threshold})")
        if anxiety_high:
            triggers.append(f"Anxiety {anxiety}/10 (threshold: {self.anxiety_threshold})")

        subject = f"Wellness Alert for {user_name} — elevated {source} scores"
        lines = [
            f"Hello,",
            f"",
            f"A wellness check for {user_name} detected elevated scores during {source} analysis.",
            f"",
            f"Triggered alerts:",
        ]
        for t in triggers:
            lines.append(f"  • {t}")
        lines.extend(["", "Details used for this assessment:", ""])

        if source == "image":
            emotions = evidence.get("detected_emotions") or []
            if emotions:
                lines.append(f"Detected emotions: {', '.join(emotions)}")
            if evidence.get("analysis"):
                lines.append(f"Analysis: {evidence['analysis']}")
            if evidence.get("recommendation"):
                lines.append(f"Recommendation: {evidence['recommendation']}")
        elif source == "chat":
            if evidence.get("message"):
                lines.append(f"User message: {evidence['message']}")

        lines.extend([
            "",
            f"Stress score:  {stress}/10",
            f"Anxiety score: {anxiety}/10",
            "",
            "Please check in with them when you can.",
            "",
            "— Wellness Tracker",
        ])
        return await self.send_email(guardian_email or "", subject, "\n".join(lines))
