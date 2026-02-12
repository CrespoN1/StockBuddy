"""
arq background tasks for AI analysis pipelines.

Each task creates its own DB session since workers run outside FastAPI's
request lifecycle. Jobs are tracked via the AnalysisJob model.
"""

import structlog
from datetime import datetime, timezone

from sqlalchemy import select

from app.database import async_session_factory
from app.models import AnalysisJob, EarningsCall
from app.services import ai_analysis, market_data, transcript, sentiment_parser
from app.services import portfolio as portfolio_svc

logger = structlog.stdlib.get_logger(__name__)


async def run_earnings_analysis(
    ctx: dict,
    job_id: str,
    user_id: str,
    ticker: str,
    transcript_text: str | None,
) -> None:
    """Background task: analyze an earnings call transcript.

    If no transcript is provided, attempts to fetch one from FMP.
    """
    async with async_session_factory() as db:
        try:
            # Load job and mark processing
            result = await db.execute(
                select(AnalysisJob).where(AnalysisJob.id == job_id)
            )
            job = result.scalars().first()
            if job is None:
                logger.error("Job %s not found", job_id)
                return

            job.status = "processing"
            job.started_at = datetime.now(timezone.utc)
            db.add(job)
            await db.flush()

            # Fetch transcript if not provided
            if not transcript_text:
                logger.info("No transcript provided for %s, fetching from FMP", ticker)
                transcript_text = await transcript.fetch_transcript(ticker)

            if not transcript_text:
                job.status = "failed"
                job.error = (
                    f"No earnings transcript available for {ticker}. "
                    "Please provide a transcript manually or ensure FMP_API_KEY is configured."
                )
                job.completed_at = datetime.now(timezone.utc)
                db.add(job)
                await db.commit()
                return

            # Get fundamentals for context
            fundamentals = await market_data.get_stock_fundamentals(ticker)

            # Run AI analysis
            analysis_text = await ai_analysis.explain_earnings_call(
                ticker=ticker,
                call_text=transcript_text,
                fundamentals=fundamentals,
            )

            # Parse structured data from AI response
            parsed = sentiment_parser.parse_analysis(analysis_text)

            # Store earnings call record with all fields populated
            ec = EarningsCall(
                user_id=user_id,
                ticker=ticker.upper(),
                extracted_text=transcript_text[:5000],
                summary=analysis_text,
                sentiment_score=parsed["sentiment_score"],
                guidance_outlook=parsed["guidance_outlook"],
                risk_mentions=parsed["risk_mentions"],
                growth_mentions=parsed["growth_mentions"],
                key_metrics=parsed["key_metrics"],
            )
            db.add(ec)

            # Update job
            job.status = "completed"
            job.result = {"analysis": analysis_text}
            job.completed_at = datetime.now(timezone.utc)
            db.add(job)
            await db.commit()

            logger.info("Earnings analysis completed for %s (job %s)", ticker, job_id)

        except Exception as exc:
            logger.exception("Earnings analysis failed for %s: %s", ticker, exc)
            await db.rollback()

            # Re-fetch job to update status
            result = await db.execute(
                select(AnalysisJob).where(AnalysisJob.id == job_id)
            )
            job = result.scalars().first()
            if job:
                job.status = "failed"
                job.error = str(exc)
                job.completed_at = datetime.now(timezone.utc)
                db.add(job)
                await db.commit()


async def run_portfolio_analysis(
    ctx: dict,
    job_id: str,
    user_id: str,
    portfolio_id: int,
) -> None:
    """Background task: full AI portfolio analysis with snapshot."""
    async with async_session_factory() as db:
        try:
            # Load job and mark processing
            result = await db.execute(
                select(AnalysisJob).where(AnalysisJob.id == job_id)
            )
            job = result.scalars().first()
            if job is None:
                logger.error("Job %s not found", job_id)
                return

            job.status = "processing"
            job.started_at = datetime.now(timezone.utc)
            db.add(job)
            await db.flush()

            # Compute snapshot
            snapshot = await portfolio_svc.analyze_portfolio(db, user_id, portfolio_id)
            sectors = await portfolio_svc.get_sector_allocation(db, user_id, portfolio_id)

            # Gather earnings summaries for holdings
            holdings = await portfolio_svc.get_holdings(db, user_id, portfolio_id)
            earnings_analyses: list[dict] = []
            for h in holdings:
                ec_result = await db.execute(
                    select(EarningsCall)
                    .where(
                        EarningsCall.holding_id == h.id,
                        EarningsCall.user_id == user_id,
                    )
                    .order_by(EarningsCall.created_at.desc())
                    .limit(1)
                )
                ec = ec_result.scalars().first()
                if ec and ec.summary:
                    earnings_analyses.append({"ticker": h.ticker, "summary": ec.summary})

            sector_dict = {s.sector: round(s.weight, 3) for s in sectors}

            portfolio_data = {
                "total_value": snapshot.total_value or 0,
                "num_positions": snapshot.num_positions,
                "health_score": snapshot.health_score or 0,
                "sector_allocation": sector_dict,
            }

            analysis_text = await ai_analysis.analyze_portfolio_with_earnings(
                portfolio_data=portfolio_data,
                earnings_analyses=earnings_analyses,
            )

            # Update job
            job.status = "completed"
            job.result = {
                "analysis": analysis_text,
                "snapshot": {
                    "total_value": snapshot.total_value,
                    "health_score": snapshot.health_score,
                    "num_positions": snapshot.num_positions,
                    "concentration_risk": snapshot.concentration_risk,
                },
            }
            job.completed_at = datetime.now(timezone.utc)
            db.add(job)
            await db.commit()

            logger.info(
                "Portfolio analysis completed for portfolio %d (job %s)",
                portfolio_id, job_id,
            )

        except Exception as exc:
            logger.exception("Portfolio analysis failed: %s", exc)
            await db.rollback()

            result = await db.execute(
                select(AnalysisJob).where(AnalysisJob.id == job_id)
            )
            job = result.scalars().first()
            if job:
                job.status = "failed"
                job.error = str(exc)
                job.completed_at = datetime.now(timezone.utc)
                db.add(job)
                await db.commit()


async def run_comparison(
    ctx: dict,
    job_id: str,
    user_id: str,
    tickers: list[str],
) -> None:
    """Background task: compare earnings calls across multiple tickers."""
    async with async_session_factory() as db:
        try:
            # Load job and mark processing
            result = await db.execute(
                select(AnalysisJob).where(AnalysisJob.id == job_id)
            )
            job = result.scalars().first()
            if job is None:
                logger.error("Job %s not found", job_id)
                return

            job.status = "processing"
            job.started_at = datetime.now(timezone.utc)
            db.add(job)
            await db.flush()

            # Gather latest earnings for each ticker
            analyses: list[dict] = []
            for ticker in tickers:
                ec_result = await db.execute(
                    select(EarningsCall)
                    .where(
                        EarningsCall.user_id == user_id,
                        EarningsCall.ticker == ticker.upper(),
                    )
                    .order_by(EarningsCall.created_at.desc())
                    .limit(1)
                )
                ec = ec_result.scalars().first()
                analyses.append(
                    {
                        "sentiment": ec.guidance_outlook or "Neutral" if ec else "No data",
                        "key_themes": ec.summary[:200] if ec and ec.summary else "",
                        "guidance": ec.guidance_outlook or "" if ec else "",
                    }
                )

            comparison_text = await ai_analysis.compare_multiple_earnings(
                tickers=tickers,
                analyses=analyses,
            )

            # Update job
            job.status = "completed"
            job.result = {"comparison": comparison_text}
            job.completed_at = datetime.now(timezone.utc)
            db.add(job)
            await db.commit()

            logger.info("Comparison completed for %s (job %s)", tickers, job_id)

        except Exception as exc:
            logger.exception("Comparison failed: %s", exc)
            await db.rollback()

            result = await db.execute(
                select(AnalysisJob).where(AnalysisJob.id == job_id)
            )
            job = result.scalars().first()
            if job:
                job.status = "failed"
                job.error = str(exc)
                job.completed_at = datetime.now(timezone.utc)
                db.add(job)
                await db.commit()
