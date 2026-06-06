from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.services.gemini_service import GeminiService
from app.services.report_service import ReportService
from app.services.email_service import EmailService
from app.services.validation_service import validate_emotion_analysis
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from typing import Dict, Any

router = APIRouter()
gemini_service = GeminiService()
report_service = ReportService()
email_service = EmailService()


def _user_display_name(user: User) -> str:
    return user.full_name or user.email


@router.post("/analyze-emotion", response_model=Dict[str, Any])
async def analyze_emotion(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Multimodal endpoint to analyze emotions from an image.
    Uses strict schema validation to prevent hallucinations.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload an image.")

    contents = await file.read()
    result = await gemini_service.analyze_emotion_multimodal(contents)
    result = validate_emotion_analysis(result)

    stress = result.get("stress_score", 0.0)
    anxiety = result.get("anxiety_score", 0.0)

    from app.models.metric import Metric
    new_metric = Metric(
        user_id=str(current_user.id),
        stress_score=stress,
        anxiety_score=anxiety,
        detected_emotions=result.get("detected_emotions", []),
        source="image"
    )
    db.add(new_metric)
    await db.commit()

    await email_service.maybe_send_threshold_alert(
        guardian_email=current_user.guardian_email,
        user_name=_user_display_name(current_user),
        source="image",
        stress=stress,
        anxiety=anxiety,
        evidence={
            "detected_emotions": result.get("detected_emotions", []),
            "analysis": result.get("analysis", ""),
            "recommendation": result.get("recommendation", ""),
        },
    )

    return result


@router.get("/reports")
async def get_weekly_report(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate weekly report and email it to the guardian automatically.
    """
    user_id = str(current_user.id)
    report = await report_service.generate_weekly_report(db, user_id)

    email_sent = False
    if current_user.guardian_email:
        email_sent = await email_service.send_weekly_report(
            current_user.guardian_email,
            _user_display_name(current_user),
            report,
        )

    report["email_sent"] = email_sent
    return report


@router.get("/metrics")
async def get_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return last 7 days of stress & anxiety per day for the dashboard chart.
    Includes dummy seed data to ensure the chart is always populated for MVP.
    """
    from datetime import datetime, timedelta
    from app.models.metric import Metric

    user_id = str(current_user.id)

    count_result = await db.execute(select(func.count()).where(Metric.user_id == user_id))
    row_count = count_result.scalar()

    if row_count < 3:
        dummy_entries = [
            Metric(user_id=user_id, stress_score=4.2, anxiety_score=3.5, source="chat", timestamp=datetime.utcnow() - timedelta(days=6)),
            Metric(user_id=user_id, stress_score=5.1, anxiety_score=4.0, source="chat", timestamp=datetime.utcnow() - timedelta(days=5)),
            Metric(user_id=user_id, stress_score=7.8, anxiety_score=6.5, source="image", timestamp=datetime.utcnow() - timedelta(days=4)),
            Metric(user_id=user_id, stress_score=6.0, anxiety_score=5.2, source="chat", timestamp=datetime.utcnow() - timedelta(days=3)),
            Metric(user_id=user_id, stress_score=4.5, anxiety_score=4.0, source="chat", timestamp=datetime.utcnow() - timedelta(days=2)),
            Metric(user_id=user_id, stress_score=3.0, anxiety_score=2.5, source="image", timestamp=datetime.utcnow() - timedelta(days=1)),
        ]
        db.add_all(dummy_entries)
        await db.commit()

    days = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day.replace(hour=23, minute=59, second=59)

        result = await db.execute(
            select(
                func.avg(Metric.stress_score).label("avg_stress"),
                func.avg(Metric.anxiety_score).label("avg_anxiety"),
            ).where(
                Metric.user_id == user_id,
                Metric.timestamp >= day_start,
                Metric.timestamp <= day_end,
            )
        )
        row = result.first()
        days.append({
            "day": day.strftime("%a"),
            "stress": round(row.avg_stress or 0.0, 1),
            "anxiety": round(row.avg_anxiety or 0.0, 1),
        })

    return days
