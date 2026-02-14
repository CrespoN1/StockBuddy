"""
Watchlist endpoints — save and track tickers outside of portfolios.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.rate_limiter import AI_LIMIT, limiter
from app.database import get_db
from app.schemas.watchlist import WatchlistItemCreate, WatchlistItemRead
from app.services import watchlist as watchlist_svc

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=list[WatchlistItemRead])
async def list_watchlist(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return await watchlist_svc.get_items(db, user_id)


@router.post("", response_model=WatchlistItemRead, status_code=201)
async def add_to_watchlist(
    body: WatchlistItemCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return await watchlist_svc.add_item(db, user_id, body.ticker)


@router.delete("/{item_id}", status_code=204)
async def remove_from_watchlist(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    deleted = await watchlist_svc.delete_item(db, user_id, item_id)
    if not deleted:
        raise HTTPException(404, "Watchlist item not found")


@router.post("/refresh", response_model=list[WatchlistItemRead])
@limiter.limit(AI_LIMIT)
async def refresh_watchlist(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return await watchlist_svc.refresh_prices(db, user_id)
