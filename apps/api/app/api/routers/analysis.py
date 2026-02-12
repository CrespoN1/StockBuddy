from arq import ArqRedis
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_arq_pool, get_current_user
from app.core.rate_limiter import AI_LIMIT, limiter
from app.database import get_db
from app.models import AnalysisJob
from app.schemas.analysis import CompareRequest, JobStatus

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.post("/portfolios/{portfolio_id}/analyze", response_model=JobStatus, status_code=202)
@limiter.limit(AI_LIMIT)
async def analyze_portfolio(
    request: Request,
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
    arq_pool: ArqRedis = Depends(get_arq_pool),
):
    """Enqueue an AI portfolio analysis as a background job.

    Returns immediately with a pending job. Poll GET /analysis/jobs/{job_id}
    for status updates.
    """
    job = AnalysisJob(
        user_id=user_id,
        job_type="portfolio_analysis",
        status="pending",
        input_data={"portfolio_id": portfolio_id},
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)

    # Enqueue background task
    await arq_pool.enqueue_job(
        "run_portfolio_analysis",
        job.id,
        user_id,
        portfolio_id,
    )

    await db.commit()
    return job


@router.post("/compare", response_model=JobStatus, status_code=202)
@limiter.limit(AI_LIMIT)
async def compare_earnings(
    request: Request,
    body: CompareRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
    arq_pool: ArqRedis = Depends(get_arq_pool),
):
    """Enqueue a multi-ticker comparison as a background job.

    Returns immediately with a pending job. Poll GET /analysis/jobs/{job_id}
    for status updates.
    """
    job = AnalysisJob(
        user_id=user_id,
        job_type="comparison",
        status="pending",
        input_data={"tickers": body.tickers},
    )
    db.add(job)
    await db.flush()
    await db.refresh(job)

    # Enqueue background task
    await arq_pool.enqueue_job(
        "run_comparison",
        job.id,
        user_id,
        body.tickers,
    )

    await db.commit()
    return job


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
