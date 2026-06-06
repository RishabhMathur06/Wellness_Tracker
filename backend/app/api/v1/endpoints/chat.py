from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.gemini_service import GeminiService
from app.services.email_service import EmailService
from app.services.pii_service import PIIService
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
gemini_service = GeminiService()
email_service = EmailService()
pii_service = PIIService()


class ChatRequest(BaseModel):
    message: str = Field(..., max_length=1000, description="The user's message")


class ChatResponse(BaseModel):
    reply: str
    pii_detected: bool = False
    pii_flags: List[str] = []
    user_message_display: Optional[str] = None
    pii_notice: Optional[str] = None


@router.post("/message", response_model=ChatResponse)
async def chat_message(
    req: ChatRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Therapeutic chat endpoint.
    PII is scanned and redacted before AI processing, storage, or guardian alerts.
    """
    scan = pii_service.scan_and_redact(req.message)
    safe_message = scan.sanitized_text

    history = []
    reply = await gemini_service.chat_therapeutic(safe_message, history)

    scores = await gemini_service.extract_scores_from_chat(safe_message)
    stress = scores["stress"]
    anxiety = scores["anxiety"]

    from app.models.metric import Metric
    notes = None
    if scan.pii_detected:
        notes = f"PII redacted: {', '.join(scan.flags)}"

    new_metric = Metric(
        user_id=str(current_user.id),
        stress_score=stress,
        anxiety_score=anxiety,
        source="chat",
        notes=notes,
    )
    db.add(new_metric)
    await db.commit()

    await email_service.maybe_send_threshold_alert(
        guardian_email=current_user.guardian_email,
        user_name=current_user.full_name or current_user.email,
        source="chat",
        stress=stress,
        anxiety=anxiety,
        evidence={"message": safe_message[:500]},
    )

    pii_notice = None
    if scan.pii_detected:
        labels = ", ".join(pii_service.flag_label(f) for f in scan.flags)
        pii_notice = (
            f"Sensitive information ({labels}) was detected and removed before processing. "
            "Please avoid sharing passwords, account numbers, or other credentials in chat."
        )

    return ChatResponse(
        reply=reply,
        pii_detected=scan.pii_detected,
        pii_flags=scan.flags,
        user_message_display=safe_message if scan.pii_detected else None,
        pii_notice=pii_notice,
    )
