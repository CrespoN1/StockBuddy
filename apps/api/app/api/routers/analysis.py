import asyncio

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.rate_limiter import AI_LIMIT, limiter
from app.database import get_db
from app.models import AnalysisJob
from app.schemas.analysis import CompareRequest, JobStatus
from app.services import portfolio as portfolio_svc
from app.services import subscription as sub_svc
from app.workers.tasks import run_portfolio_analysis, run_comparison

logger = structlog.stdlib.get_logger(__name__)


def _log_task_exception(task: asyncio.Task) -> None:
    if task.cancelled():
        return
    exc = task.exception()
    if exc:
        logger.error("Background task failed", error=str(exc), exc_info=exc)


router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/portfolios/{portfolio_id}/analyze", response_model=JobStatus, status_code=202)
@limiter.limit(AI_LIMIT)
async def analyze_portfolio(
    request: Request,
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Start an AI portfolio analysis as a background task.

    Returns immediately with a pending job. Poll GET /analysis/jobs/{job_id}
    for status updates.
    """
    portfolio = await portfolio_svc.get_portfolio(db, user_id, portfolio_id)
    if portfolio is None:
        raise HTTPException(404, "Portfolio not found")

    if not await sub_svc.check_can_analyze_portfolio(db, user_id):
        raise HTTPException(
            403,
            "Free plan allows 1 portfolio analysis per month. Upgrade to Pro for unlimited.",
        )

    job = AnalysisJob(
        user_id=user_id,
        job_type="portfolio_analysis",
        status="pending",
        input_data={"portfolio_id": portfolio_id},
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    await db.commit()

    # Run as inline background task (no separate worker needed)
    task = asyncio.create_task(
        run_portfolio_analysis({}, str(job.id), user_id, portfolio_id)
    )
    task.add_done_callback(_log_task_exception)

    return job


@router.post("/compare", response_model=JobStatus, status_code=202)
@limiter.limit(AI_LIMIT)
async def compare_earnings(
    request: Request,
    body: CompareRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Start a multi-ticker comparison as a background task.

    Returns immediately with a pending job. Poll GET /analysis/jobs/{job_id}
    for status updates.
    """
    if not await sub_svc.check_can_compare(db, user_id):
        raise HTTPException(
            403, "Stock comparison requires Pro plan. Upgrade to unlock."
        )

    job = AnalysisJob(
        user_id=user_id,
        job_type="comparison",
        status="pending",
        input_data={"tickers": body.tickers},
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)
    await db.commit()

    # Run as inline background task (no separate worker needed)
    task = asyncio.create_task(
        run_comparison({}, str(job.id), user_id, body.tickers)
    )
    task.add_done_callback(_log_task_exception)

    return job


# ─── Past comparisons ────────────────────────────────────────────────

@router.get("/comparisons", response_model=list[JobStatus])
async def list_comparisons(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """List completed comparison jobs for the current user."""
    result = await db.execute(
        select(AnalysisJob)
        .where(
            AnalysisJob.user_id == user_id,
            AnalysisJob.job_type == "comparison",
            AnalysisJob.status == "completed",
        )
        .order_by(AnalysisJob.completed_at.desc())
        .limit(20)
    )
    return list(result.scalars().all())


# ─── Job status polling ───────────────────────────────────────────────

@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(
    job_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    result = await db.execute(
        select(AnalysisJob).where(
            AnalysisJob.id == job_id,
            AnalysisJob.user_id == user_id,
        )
    )
    job = result.scalars().first()
    if job is None:
        raise HTTPException(404, "Job not found")
    return job
