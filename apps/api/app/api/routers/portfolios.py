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
from app.services import portfolio as portfolio_svc

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
    return await portfolio_svc.analyze_portfolio(db, user_id, portfolio_id)


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
