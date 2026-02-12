from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.rate_limiter import AI_LIMIT, limiter
from app.database import get_db
from app.schemas.holding import HoldingCreate, HoldingRead, HoldingUpdate
from app.services import portfolio as portfolio_svc

router = APIRouter(prefix="/portfolios/{portfolio_id}/holdings", tags=["holdings"])


@router.get("", response_model=list[HoldingRead])
async def list_holdings(
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return await portfolio_svc.get_holdings(db, user_id, portfolio_id)


@router.post("", response_model=HoldingRead, status_code=201)
async def add_holding(
    portfolio_id: int,
    body: HoldingCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    holding = await portfolio_svc.add_holding(
        db, user_id, portfolio_id, body.ticker, body.shares
    )
    if holding is None:
        raise HTTPException(404, "Portfolio not found")
    return holding


@router.put("/{holding_id}", response_model=HoldingRead)
async def update_holding(
    portfolio_id: int,
    holding_id: int,
    body: HoldingUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    holding = await portfolio_svc.update_holding(
        db, user_id, portfolio_id, holding_id, body.shares
    )
    if holding is None:
        raise HTTPException(404, "Holding not found")
    return holding


@router.delete("/{holding_id}", status_code=204)
async def delete_holding(
    portfolio_id: int,
    holding_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    deleted = await portfolio_svc.delete_holding(db, user_id, portfolio_id, holding_id)
    if not deleted:
        raise HTTPException(404, "Holding not found")


@router.post("/refresh", response_model=list[HoldingRead])
@limiter.limit(AI_LIMIT)
async def refresh_holdings(
    request: "Request",
    portfolio_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Refresh market data (price, sector, beta) for all holdings in a portfolio."""
    holdings = await portfolio_svc.refresh_holdings(db, user_id, portfolio_id)
    if holdings is None:
        raise HTTPException(404, "Portfolio not found")
    return holdings
