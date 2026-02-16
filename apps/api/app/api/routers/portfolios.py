import asyncio

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
    DashboardSummary,
    EarningsInsights,
    PortfolioHistoryWithBenchmark,
    PortfolioSnapshotRead,
    SectorAllocation,
)
from app.schemas.holding import HoldingRead
from app.schemas.stock import NewsArticle, RedditPost
from app.services import news, reddit, portfolio as portfolio_svc, stock_data
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


@router.get("/earnings-calendar", response_model=list[HoldingRead])
async def get_earnings_calendar(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Return all holdings with upcoming earnings dates."""
    return await portfolio_svc.get_earnings_calendar(db, user_id)


@router.get("/dashboard-summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Compute dashboard summary: best/worst performer + upcoming earnings."""
    return await portfolio_svc.get_dashboard_summary(db, user_id)


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

@router.get("/{portfolio_id}/history", response_model=list[PortfolioSnapshotRead])
async def get_portfolio_history(
    portfolio_id: int,
    days: int = 90,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return await portfolio_svc.get_snapshot_history(db, user_id, portfolio_id, days)


@router.get(
    "/{portfolio_id}/history-with-benchmark",
    response_model=PortfolioHistoryWithBenchmark,
)
async def get_portfolio_history_with_benchmark(
    portfolio_id: int,
    days: int = 90,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Return portfolio % change alongside S&P 500 % change.

    If holdings have purchased_at dates, reconstructs history from yfinance.
    Otherwise falls back to snapshot-based history.
    """
    from datetime import timedelta, datetime as dt
    from app.schemas.analysis import BenchmarkPoint

    # ── Try reconstructed history first ──────────────────────────────
    reconstructed = await portfolio_svc.reconstruct_portfolio_history(
        db, user_id, portfolio_id
    )

    if reconstructed and len(reconstructed) >= 2:
        start_str = reconstructed[0]["date"]
        end_str = reconstructed[-1]["date"]

        spy_bars = await stock_data.get_benchmark_history(start_str, end_str)
        spy_by_date: dict[str, float] = {b["date"]: b["close"] for b in spy_bars}
        spy_dates_sorted = sorted(spy_by_date.keys())

        base_spy = spy_by_date.get(spy_dates_sorted[0], 0) if spy_dates_sorted else 0
        first_cost = reconstructed[0].get("cost", 0)

        if first_cost > 0 and base_spy > 0:
            data: list[BenchmarkPoint] = []
            last_spy_close = base_spy

            for point in reconstructed:
                d = point["date"]
                cost = point.get("cost", 0)
                # Gain on invested capital — immune to new-holding additions
                if cost > 0:
                    portfolio_pct = ((point["value"] - cost) / cost) * 100
                else:
                    portfolio_pct = 0.0

                spy_close = spy_by_date.get(d)
                if spy_close is None:
                    for sd in reversed(spy_dates_sorted):
                        if sd <= d:
                            spy_close = spy_by_date[sd]
                            break
                if spy_close is None:
                    spy_close = last_spy_close
                last_spy_close = spy_close

                sp500_pct = ((spy_close - base_spy) / base_spy) * 100

                date_obj = dt.strptime(d, "%Y-%m-%d")
                data.append(
                    BenchmarkPoint(
                        date=date_obj.strftime("%b %d"),
                        portfolio_pct=round(portfolio_pct, 2),
                        sp500_pct=round(sp500_pct, 2),
                    )
                )

            # Downsample if too many points (keep chart responsive)
            if len(data) > 120:
                step = len(data) // 90
                data = data[::step] + [data[-1]]

            return PortfolioHistoryWithBenchmark(data=data)

    # ── Fallback: snapshot-based history ─────────────────────────────
    snapshots = await portfolio_svc.get_snapshot_history(
        db, user_id, portfolio_id, days
    )
    if len(snapshots) < 2:
        return PortfolioHistoryWithBenchmark(data=[])

    start_dt = snapshots[0].created_at
    end_dt = snapshots[-1].created_at + timedelta(days=1)
    start_str_snap = start_dt.strftime("%Y-%m-%d")
    end_str_snap = end_dt.strftime("%Y-%m-%d")

    spy_bars_snap = await stock_data.get_benchmark_history(start_str_snap, end_str_snap)
    spy_by_date_snap: dict[str, float] = {b["date"]: b["close"] for b in spy_bars_snap}

    base_portfolio_snap = snapshots[0].total_value or 0
    spy_dates_sorted_snap = sorted(spy_by_date_snap.keys())
    base_spy_snap = spy_by_date_snap[spy_dates_sorted_snap[0]] if spy_dates_sorted_snap else 0

    if base_portfolio_snap == 0 or base_spy_snap == 0:
        return PortfolioHistoryWithBenchmark(data=[])

    fallback_data: list[BenchmarkPoint] = []
    last_spy_snap = base_spy_snap

    for snap in snapshots:
        snap_date = snap.created_at.strftime("%Y-%m-%d")
        portfolio_val = snap.total_value or 0
        portfolio_pct = ((portfolio_val - base_portfolio_snap) / base_portfolio_snap) * 100

        spy_close = spy_by_date_snap.get(snap_date)
        if spy_close is None:
            for d in reversed(spy_dates_sorted_snap):
                if d <= snap_date:
                    spy_close = spy_by_date_snap[d]
                    break
        if spy_close is None:
            spy_close = last_spy_snap
        last_spy_snap = spy_close

        sp500_pct = ((spy_close - base_spy_snap) / base_spy_snap) * 100

        fallback_data.append(
            BenchmarkPoint(
                date=snap.created_at.strftime("%b %d"),
                portfolio_pct=round(portfolio_pct, 2),
                sp500_pct=round(sp500_pct, 2),
            )
        )

    return PortfolioHistoryWithBenchmark(data=fallback_data)


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


@router.get("/{portfolio_id}/reddit", response_model=list[RedditPost])
async def get_portfolio_reddit(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Get aggregated Reddit posts for all holdings in a portfolio."""
    portfolio = await portfolio_svc.get_portfolio(db, user_id, portfolio_id)
    if portfolio is None:
        raise HTTPException(404, "Portfolio not found")

    holdings = await portfolio_svc.get_holdings(db, user_id, portfolio_id)
    if not holdings:
        return []

    all_posts: list[dict] = []
    for h in holdings[:10]:  # cap at 10 holdings to respect rate limits
        posts = await reddit.get_reddit_posts(h.ticker, limit=5)
        all_posts.extend(posts)
        await asyncio.sleep(0.5)  # rate limit courtesy delay

    # Sort by created_utc descending (most recent first)
    all_posts.sort(key=lambda x: x.get("created_utc", 0), reverse=True)

    return all_posts[:50]
