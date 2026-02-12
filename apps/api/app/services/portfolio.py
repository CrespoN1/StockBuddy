"""
Portfolio CRUD and analysis logic.

Migrated from: portfolio_analyzer.py (original StockBuddy)
Changes: in-memory state → DB-backed via SQLModel, all queries scoped by user_id,
         duplicate get_earnings_insights resolved (kept first version with sentiment_summary).
"""

import asyncio
import structlog
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import EarningsCall, Holding, Portfolio, PortfolioSnapshot
from app.schemas.analysis import EarningsInsights, SectorAllocation
from app.services import market_data

logger = structlog.stdlib.get_logger(__name__)


# ─── CRUD ─────────────────────────────────────────────────────────────

async def create_portfolio(db: AsyncSession, user_id: str, name: str) -> Portfolio:
    portfolio = Portfolio(user_id=user_id, name=name)
    db.add(portfolio)
    await db.flush()
    await db.refresh(portfolio)
    return portfolio


async def get_portfolios(db: AsyncSession, user_id: str) -> list[Portfolio]:
    result = await db.execute(
        select(Portfolio).where(Portfolio.user_id == user_id).order_by(Portfolio.created_at.desc())
    )
    return list(result.scalars().all())


async def get_portfolio(db: AsyncSession, user_id: str, portfolio_id: int) -> Portfolio | None:
    result = await db.execute(
        select(Portfolio)
        .where(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
        .options(selectinload(Portfolio.holdings))
    )
    return result.scalars().first()


async def update_portfolio(
    db: AsyncSession, user_id: str, portfolio_id: int, name: str
) -> Portfolio | None:
    portfolio = await get_portfolio(db, user_id, portfolio_id)
    if portfolio is None:
        return None
    portfolio.name = name
    portfolio.updated_at = datetime.now(timezone.utc)
    db.add(portfolio)
    await db.flush()
    await db.refresh(portfolio)
    return portfolio


async def delete_portfolio(db: AsyncSession, user_id: str, portfolio_id: int) -> bool:
    portfolio = await get_portfolio(db, user_id, portfolio_id)
    if portfolio is None:
        return False
    await db.delete(portfolio)
    await db.flush()
    return True


# ─── Holdings ─────────────────────────────────────────────────────────

async def add_holding(
    db: AsyncSession, user_id: str, portfolio_id: int, ticker: str, shares: float
) -> Holding | None:
    """Add a holding and populate market data from Alpha Vantage."""
    # Verify portfolio belongs to user
    portfolio = await get_portfolio(db, user_id, portfolio_id)
    if portfolio is None:
        return None

    ticker = ticker.upper()

    # Fetch market data — price and fundamentals independently so a rate-limit
    # on one call doesn't lose the other's data.
    last_price = 0.0
    sector: str | None = "Unknown"
    beta: float | None = 1.0
    dividend_yield: float | None = None

    try:
        price = await market_data.get_latest_price(ticker)
        last_price = price or 0.0
    except Exception as exc:
        logger.warning("Price fetch failed for %s: %s", ticker, exc)

    await asyncio.sleep(1.5)  # respect Alpha Vantage rate limit

    try:
        fundamentals = await market_data.get_stock_fundamentals(ticker)
        sector = fundamentals.get("sector") or "Unknown"
        beta = fundamentals.get("beta") or 1.0
        dividend_yield = fundamentals.get("dividend_yield")
    except Exception as exc:
        logger.warning("Fundamentals fetch failed for %s: %s", ticker, exc)

    holding = Holding(
        user_id=user_id,
        portfolio_id=portfolio_id,
        ticker=ticker,
        shares=shares,
        last_price=last_price,
        sector=sector,
        beta=beta,
        dividend_yield=dividend_yield,
    )
    db.add(holding)
    await db.flush()
    await db.refresh(holding)
    return holding


async def refresh_holdings(
    db: AsyncSession, user_id: str, portfolio_id: int
) -> list[Holding] | None:
    """Refresh prices for all holdings in a portfolio.

    Adds a 1.5s delay between API calls to respect Alpha Vantage free-tier
    rate limits (5 requests/minute, 25/day).
    """
    portfolio = await get_portfolio(db, user_id, portfolio_id)
    if portfolio is None:
        return None

    holdings = await get_holdings(db, user_id, portfolio_id)
    for i, h in enumerate(holdings):
        if i > 0:
            await asyncio.sleep(1.5)
        try:
            price = await market_data.get_latest_price(h.ticker)
            if price is not None:
                h.last_price = price
                h.updated_at = datetime.now(timezone.utc)
                db.add(h)
        except Exception as exc:
            logger.warning("Price refresh failed for %s: %s", h.ticker, exc)

    await db.flush()
    for h in holdings:
        await db.refresh(h)
    return holdings


async def get_holdings(db: AsyncSession, user_id: str, portfolio_id: int) -> list[Holding]:
    result = await db.execute(
        select(Holding).where(
            Holding.user_id == user_id,
            Holding.portfolio_id == portfolio_id,
        )
    )
    return list(result.scalars().all())


async def update_holding(
    db: AsyncSession, user_id: str, portfolio_id: int, holding_id: int, shares: float
) -> Holding | None:
    result = await db.execute(
        select(Holding).where(
            Holding.id == holding_id,
            Holding.user_id == user_id,
            Holding.portfolio_id == portfolio_id,
        )
    )
    holding = result.scalars().first()
    if holding is None:
        return None
    holding.shares = shares
    holding.updated_at = datetime.now(timezone.utc)
    db.add(holding)
    await db.flush()
    await db.refresh(holding)
    return holding


async def delete_holding(
    db: AsyncSession, user_id: str, portfolio_id: int, holding_id: int
) -> bool:
    result = await db.execute(
        select(Holding).where(
            Holding.id == holding_id,
            Holding.user_id == user_id,
            Holding.portfolio_id == portfolio_id,
        )
    )
    holding = result.scalars().first()
    if holding is None:
        return False
    await db.delete(holding)
    await db.flush()
    return True


# ─── Analysis (ported from portfolio_analyzer.py) ─────────────────────

def calculate_health_score(
    concentration_risk: float,
    num_positions: int,
    avg_sentiment: float,
    total_value: float,
) -> int:
    """Calculate portfolio health score 0-100.

    Ported directly from PortfolioAnalyzer._calculate_health_score.
    """
    score = 100

    # Concentration penalty
    if concentration_risk > 0.35:
        score -= 30
    elif concentration_risk > 0.25:
        score -= 20
    elif concentration_risk > 0.15:
        score -= 10

    # Position count
    if num_positions < 5:
        score -= 15
    elif num_positions < 10:
        score -= 5

    # Sentiment bonus/penalty
    if avg_sentiment > 0.3:
        score += 10
    elif avg_sentiment < -0.2:
        score -= 15

    # Value bonus
    if total_value > 100_000:
        score += 5
    elif total_value < 10_000:
        score -= 5

    return max(0, min(100, score))


async def analyze_portfolio(
    db: AsyncSession, user_id: str, portfolio_id: int
) -> PortfolioSnapshot:
    """Run portfolio analysis and persist a snapshot.

    Ported from PortfolioAnalyzer.analyze_portfolio.
    """
    holdings = await get_holdings(db, user_id, portfolio_id)

    if not holdings:
        snapshot = PortfolioSnapshot(
            user_id=user_id,
            portfolio_id=portfolio_id,
            num_positions=0,
            health_score=0,
        )
        db.add(snapshot)
        await db.flush()
        await db.refresh(snapshot)
        return snapshot

    # Calculate total value & weights
    total_value = sum(
        (h.last_price or 0) * h.shares for h in holdings
    )

    weights = []
    for h in holdings:
        val = (h.last_price or 0) * h.shares
        weights.append(val / total_value if total_value > 0 else 0)

    concentration_risk = max(weights) if weights else 0.0

    # Sentiment from earnings calls
    sentiment_scores: list[float] = []
    for h in holdings:
        result = await db.execute(
            select(EarningsCall)
            .where(EarningsCall.holding_id == h.id, EarningsCall.user_id == user_id)
            .order_by(EarningsCall.created_at.desc())
            .limit(1)
        )
        latest_ec = result.scalars().first()
        if latest_ec and latest_ec.sentiment_score is not None:
            sentiment_scores.append(latest_ec.sentiment_score)

    avg_sentiment = (
        sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
    )
    earnings_coverage = len(sentiment_scores) / len(holdings) if holdings else 0.0

    health_score = calculate_health_score(
        concentration_risk=concentration_risk,
        num_positions=len(holdings),
        avg_sentiment=avg_sentiment,
        total_value=total_value,
    )

    snapshot = PortfolioSnapshot(
        user_id=user_id,
        portfolio_id=portfolio_id,
        total_value=total_value,
        num_positions=len(holdings),
        recent_earnings_coverage=earnings_coverage,
        avg_sentiment_score=avg_sentiment if sentiment_scores else None,
        concentration_risk=concentration_risk,
        health_score=health_score,
    )
    db.add(snapshot)
    await db.flush()
    await db.refresh(snapshot)
    return snapshot


async def get_sector_allocation(
    db: AsyncSession, user_id: str, portfolio_id: int
) -> list[SectorAllocation]:
    """Calculate sector allocation.

    Ported from PortfolioAnalyzer.get_sector_allocation.
    """
    holdings = await get_holdings(db, user_id, portfolio_id)
    total_value = sum((h.last_price or 0) * h.shares for h in holdings)

    if total_value == 0:
        return []

    sector_totals: dict[str, float] = {}
    for h in holdings:
        val = (h.last_price or 0) * h.shares
        sector = h.sector or "Unknown"
        sector_totals[sector] = sector_totals.get(sector, 0) + val

    return [
        SectorAllocation(sector=sector, weight=val / total_value, value=round(val, 2))
        for sector, val in sorted(sector_totals.items(), key=lambda x: -x[1])
    ]


async def get_earnings_insights(
    db: AsyncSession, user_id: str, portfolio_id: int
) -> EarningsInsights:
    """Get earnings-based insights for all holdings.

    Ported from PortfolioAnalyzer.get_earnings_insights (first version, lines 157-195).
    The duplicate at line 231 is intentionally discarded.
    """
    holdings = await get_holdings(db, user_id, portfolio_id)

    insights = EarningsInsights(
        sentiment_summary={"positive": 0, "neutral": 0, "negative": 0, "no_data": 0}
    )

    for h in holdings:
        # Get latest earnings call for this holding
        result = await db.execute(
            select(EarningsCall)
            .where(EarningsCall.holding_id == h.id, EarningsCall.user_id == user_id)
            .order_by(EarningsCall.created_at.desc())
            .limit(1)
        )
        latest = result.scalars().first()

        if latest:
            insights.holdings_with_recent_earnings.append(h.ticker)
            sentiment = latest.sentiment_score or 0.0

            if sentiment > 0.2:
                insights.positive_outlooks.append(h.ticker)
                insights.sentiment_summary["positive"] += 1
            elif sentiment < -0.1:
                insights.risk_warnings.append(h.ticker)
                insights.sentiment_summary["negative"] += 1
            else:
                insights.sentiment_summary["neutral"] += 1
        else:
            insights.sentiment_summary["no_data"] += 1

    return insights
