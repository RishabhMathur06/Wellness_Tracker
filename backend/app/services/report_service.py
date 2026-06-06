from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from app.models.metric import Metric
from typing import Dict, Any

class ReportService:
    def __init__(self):
        pass

    async def generate_weekly_report(self, db: AsyncSession, user_id: str) -> Dict[str, Any]:
        """
        Aggregate the past week's metrics and generate a summary.
        Efficiency: Use SQL aggregation where possible instead of loading all rows.
        """
        # For MVP, we'll calculate simple averages over all records for the user
        result = await db.execute(
            select(
                func.avg(Metric.stress_score).label("avg_stress"),
                func.avg(Metric.anxiety_score).label("avg_anxiety")
            ).where(Metric.user_id == user_id)
        )
        row = result.first()
        
        avg_stress = round(row.avg_stress or 0.0, 1) if row else 0.0
        avg_anxiety = round(row.avg_anxiety or 0.0, 1) if row else 0.0
        
        # Logic to suggest doctors or solutions based on scores
        summary = "Overall stable week."
        if avg_stress > 7.0 or avg_anxiety > 7.0:
            summary = "High stress/anxiety detected over the week. It is highly recommended to consult a mental health professional or therapist."
            
        return {
            "avg_stress": avg_stress,
            "avg_anxiety": avg_anxiety,
            "summary": summary
        }
