import asyncio
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.rate_limiter import AI_LIMIT, limiter
from app.database import get_db
from app.models import AnalysisJob, EarningsCall
from app.schemas.analysis import JobStatus
from app.schemas.earnings import EarningsAnalyzeRequest, EarningsCallRead
from app.services import subscription as sub_svc
from app.workers.tasks import run_earnings_analysis

logger = structlog.stdlib.get_logger(__name__)


def _log_task_exception(task: asyncio.Task) -> None:
    if task.cancelled():
        return
    exc = task.exception()
    if exc:
        logger.error("Background task failed", error=str(exc), exc_info=exc)


router = APIRouter(prefix="/stocks/{ticker}/earnings", tags=["earnings"])


@router.get("", response_model=list[EarningsCallRead])
async def list_earnings(
    ticker: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    result = await db.execute(
        select(EarningsCall)
        .where(
            EarningsCall.user_id == user_id,
            EarningsCall.ticker == ticker.upper(),
        )
        .order_by(EarningsCall.created_at.desc())
    )
    return list(result.scalars().all())


@router.post("/analyze", response_model=JobStatus, status_code=202)
@limiter.limit(AI_LIMIT)
async def analyze_earnings(
    request: Request,
    ticker: str,
    body: EarningsAnalyzeRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Start an AI earnings analysis as a background task.

    Returns immediately with a pending job. Poll GET /analysis/jobs/{job_id}
    for status updates.
    """
    if not await sub_svc.check_can_analyze_earnings(db, user_id):
        raise HTTPException(
            403,
            "Free plan allows 3 earnings analyses per month. Upgrade to Pro for unlimited.",
        )
    job = AnalysisJob(
        user_id=user_id,
        job_type="earnings_analysis",
        status="pending",
        input_data={
            "ticker": ticker.upper(),
            "has_transcript": body.transcript is not None,
        },
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    await db.commit()

    # Run as inline background task (no separate worker needed)
    task = asyncio.create_task(
        run_earnings_analysis(
            {}, str(job.id), user_id, ticker.upper(), body.transcript
        )
    )
    task.add_done_callback(_log_task_exception)

    return job
