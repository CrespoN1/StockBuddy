from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.schemas.portfolio import (
    PortfolioCreate,
    PortfolioDetail,
    PortfolioRead,
    PortfolioUpdate,
)
from app.schemas.analysis import (
    EarningsInsights,
    PortfolioSnapshotRead,
    SectorAllocation,
)
from app.schemas.stock import NewsArticle
from app.services import news, portfolio as portfolio_svc
from app.services import subscription as sub_svc

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.get("", response_model=list[PortfolioRead])
async def list_portfolios(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return await portfolio_svc.get_portfolios(db, user_id)


@router.post("", response_model=PortfolioRead, status_code=201)
async def create_portfolio(
    body: PortfolioCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    if not await sub_svc.check_can_create_portfolio(db, user_id):
        raise HTTPException(
            403, "Free plan allows only 1 portfolio. Upgrade to Pro for unlimited."
        )
    return await portfolio_svc.create_portfolio(db, user_id, body.name)


@router.get("/{portfolio_id}", response_model=PortfolioDetail)
async def get_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    portfolio = await portfolio_svc.get_portfolio(db, user_id, portfolio_id)
    if portfolio is None:
        raise HTTPException(404, "Portfolio not found")
    return portfolio


@router.put("/{portfolio_id}", response_model=PortfolioRead)
async def update_portfolio(
    portfolio_id: int,
    body: PortfolioUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    portfolio = await portfolio_svc.update_portfolio(db, user_id, portfolio_id, body.name)
    if portfolio is None:
        raise HTTPException(404, "Portfolio not found")
    return portfolio


@router.delete("/{portfolio_id}", status_code=204)
async def delete_portfolio(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    deleted = await portfolio_svc.delete_portfolio(db, user_id, portfolio_id)
    if not deleted:
        raise HTTPException(404, "Portfolio not found")


# ─── Analysis endpoints under /portfolios/{id}/ ──────────────────────

@router.get("/{portfolio_id}/snapshot", response_model=PortfolioSnapshotRead)
async def get_portfolio_snapshot(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    snapshot = await portfolio_svc.analyze_portfolio(db, user_id, portfolio_id)
    holdings = await portfolio_svc.get_holdings(db, user_id, portfolio_id)
    daily_change, daily_change_pct = portfolio_svc.compute_daily_change(holdings)

    result = PortfolioSnapshotRead.model_validate(snapshot)
    result.daily_change = daily_change
    result.daily_change_pct = daily_change_pct
    return result


@router.get("/{portfolio_id}/sectors", response_model=list[SectorAllocation])
async def get_sector_allocation(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return await portfolio_svc.get_sector_allocation(db, user_id, portfolio_id)


@router.get("/{portfolio_id}/earnings-insights", response_model=EarningsInsights)
async def get_earnings_insights(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return await portfolio_svc.get_earnings_insights(db, user_id, portfolio_id)


@router.get("/{portfolio_id}/news", response_model=list[NewsArticle])
async def get_portfolio_news(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Get aggregated news for all holdings in a portfolio."""
    portfolio = await portfolio_svc.get_portfolio(db, user_id, portfolio_id)
    if portfolio is None:
        raise HTTPException(404, "Portfolio not found")

    holdings = await portfolio_svc.get_holdings(db, user_id, portfolio_id)
    if not holdings:
        return []

    # Fetch 5 articles per holding, merge and sort by date
    all_articles: list[dict] = []
    for h in holdings[:10]:  # cap at 10 holdings to avoid rate limits
        articles = await news.get_stock_news(h.ticker, limit=5)
        all_articles.extend(articles)

    # Sort by published_at descending and deduplicate by title
    seen_titles: set[str] = set()
    unique: list[dict] = []
    for a in sorted(all_articles, key=lambda x: x.get("published_at", ""), reverse=True):
        if a["title"] not in seen_titles:
            seen_titles.add(a["title"])
            unique.append(a)

    return unique[:20]  # Return top 20 most recent
