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
from app.services import ai_analysis, market_data, transcript, sentiment_parser, news
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


async def _ensure_earnings_data(
    db, user_id: str, ticker: str
) -> EarningsCall | None:
    """Check DB for existing earnings data; if missing, gather data and analyze.

    Data sources (tried in order):
    1. Existing EarningsCall in DB
    2. FMP earnings transcript (if FMP_API_KEY configured)
    3. Alpha Vantage fundamentals + news sentiment (fallback — always available)

    Returns the EarningsCall record (existing or newly created), or None on failure.
    """
    ticker = ticker.upper()

    # 1. Check for existing earnings analysis
    ec_result = await db.execute(
        select(EarningsCall)
        .where(
            EarningsCall.user_id == user_id,
            EarningsCall.ticker == ticker,
        )
        .order_by(EarningsCall.created_at.desc())
        .limit(1)
    )
    ec = ec_result.scalars().first()
    if ec and ec.summary:
        logger.info("Found existing earnings data for %s", ticker)
        return ec

    # 2. Try FMP transcript first (best data source)
    transcript_text = None
    try:
        transcript_text = await transcript.fetch_transcript(ticker)
    except Exception as exc:
        logger.warning("Failed to fetch transcript for %s: %s", ticker, exc)

    # 3. Get fundamentals (always available via Alpha Vantage)
    fundamentals = await market_data.get_stock_fundamentals(ticker)

    if transcript_text:
        # Have real transcript — run full earnings analysis
        logger.info("Analyzing FMP transcript for %s", ticker)
        analysis_text = await ai_analysis.explain_earnings_call(
            ticker=ticker,
            call_text=transcript_text,
            fundamentals=fundamentals,
        )
    else:
        # No transcript — build analysis from fundamentals + news sentiment
        logger.info("No transcript for %s, building analysis from fundamentals + news", ticker)

        # Fetch recent news with sentiment scores
        news_articles = await news.get_stock_news(ticker, limit=10)

        # Build a data summary for the AI
        news_summary = ""
        if news_articles:
            for i, article in enumerate(news_articles[:8], 1):
                news_summary += (
                    f"  {i}. [{article.get('ticker_sentiment_label', 'Neutral')} "
                    f"(score: {article.get('ticker_sentiment_score', 0):.2f})] "
                    f"{article.get('title', 'N/A')}\n"
                    f"     Summary: {article.get('summary', '')[:150]}\n"
                )
        else:
            news_summary = "  No recent news available.\n"

        # Get current price
        price = await market_data.get_latest_price(ticker)
        price_str = f"${price:.2f}" if price is not None else "N/A"

        analysis_context = f"""
Stock: {ticker}
Current Price: {price_str}
Sector: {fundamentals.get('sector', 'N/A')}
Market Cap: {fundamentals.get('market_cap', 'N/A')}
P/E Ratio: {fundamentals.get('pe_ratio', 'N/A')}
Beta: {fundamentals.get('beta', 'N/A')}
Dividend Yield: {fundamentals.get('dividend_yield', 'N/A')}

Recent News & Sentiment:
{news_summary}
"""

        analysis_text = await ai_analysis.analyze_stock_overview(
            ticker=ticker,
            context=analysis_context,
        )

    # 4. Parse structured data
    parsed = sentiment_parser.parse_analysis(analysis_text)

    # 5. Store in DB for future use
    ec = EarningsCall(
        user_id=user_id,
        ticker=ticker,
        extracted_text=(transcript_text or "Generated from fundamentals + news")[:5000],
        summary=analysis_text,
        sentiment_score=parsed["sentiment_score"],
        guidance_outlook=parsed["guidance_outlook"],
        risk_mentions=parsed["risk_mentions"],
        growth_mentions=parsed["growth_mentions"],
        key_metrics=parsed["key_metrics"],
    )
    db.add(ec)
    await db.flush()

    logger.info("Created new earnings analysis for %s", ticker)
    return ec


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

            # Gather earnings summaries for holdings (fetch from FMP if missing)
            holdings = await portfolio_svc.get_holdings(db, user_id, portfolio_id)
            earnings_analyses: list[dict] = []
            for h in holdings:
                ec = await _ensure_earnings_data(db, user_id, h.ticker)
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
    """Background task: compare earnings calls across multiple tickers.

    For each ticker, ensures we have real earnings data by fetching
    transcripts from FMP if no prior analysis exists.
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

            # Gather real earnings data for each ticker (fetch if missing)
            analyses: list[dict] = []
            for ticker in tickers:
                ec = await _ensure_earnings_data(db, user_id, ticker.upper())
                if ec and ec.summary:
                    analyses.append(
                        {
                            "sentiment": ec.guidance_outlook or "Neutral",
                            "key_themes": ec.summary[:500],
                            "guidance": ec.guidance_outlook or "",
                        }
                    )
                else:
                    analyses.append(
                        {
                            "sentiment": "No transcript available",
                            "key_themes": "",
                            "guidance": "",
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
