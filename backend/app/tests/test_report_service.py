import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.services.report_service import ReportService
from app.models.metric import Metric


@pytest.mark.asyncio
async def test_generate_weekly_report_averages_metrics(db_engine):
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as db:
        db.add(Metric(user_id="1", stress_score=4.0, anxiety_score=2.0, source="chat"))
        db.add(Metric(user_id="1", stress_score=8.0, anxiety_score=6.0, source="chat"))
        await db.commit()

        service = ReportService()
        report = await service.generate_weekly_report(db, "1")

    assert report["avg_stress"] == 6.0
    assert report["avg_anxiety"] == 4.0
    assert "summary" in report


@pytest.mark.asyncio
async def test_generate_weekly_report_high_stress_summary(db_engine):
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as db:
        db.add(Metric(user_id="2", stress_score=9.0, anxiety_score=8.0, source="image"))
        await db.commit()

        service = ReportService()
        report = await service.generate_weekly_report(db, "2")

    assert report["avg_stress"] == 9.0
    assert "high stress" in report["summary"].lower() or "recommended" in report["summary"].lower()
