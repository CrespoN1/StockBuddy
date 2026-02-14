"""
Watchlist CRUD and price refresh.
"""

import asyncio
import structlog
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WatchlistItem
from app.services import market_data

logger = structlog.stdlib.get_logger(__name__)


async def add_item(
    db: AsyncSession, user_id: str, ticker: str
) -> WatchlistItem:
    """Add a ticker to the watchlist. Fetches price and fundamentals."""
    ticker = ticker.upper()

    # Check for duplicate
    result = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.user_id == user_id,
            WatchlistItem.ticker == ticker,
        )
    )
    existing = result.scalars().first()
    if existing is not None:
        return existing

    # Fetch price + previous close
    last_price: float | None = None
    previous_close: float | None = None
    try:
        quote = await market_data.get_quote(ticker)
        last_price = quote["price"]
        previous_close = quote["previous_close"]
    except Exception as exc:
        logger.warning("Quote fetch failed for %s: %s", ticker, exc)

    await asyncio.sleep(1.5)  # respect Alpha Vantage rate limit

    # Fetch fundamentals for name + sector
    name: str | None = None
    sector: str | None = None
    try:
        fundamentals = await market_data.get_stock_fundamentals(ticker)
        sector = fundamentals.get("sector") or None
        name = fundamentals.get("name") or None
    except Exception as exc:
        logger.warning("Fundamentals fetch failed for %s: %s", ticker, exc)

    item = WatchlistItem(
        user_id=user_id,
        ticker=ticker,
        name=name,
        last_price=last_price,
        previous_close=previous_close,
        sector=sector,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


async def get_items(db: AsyncSession, user_id: str) -> list[WatchlistItem]:
    """Get all watchlist items for a user."""
    result = await db.execute(
        select(WatchlistItem)
        .where(WatchlistItem.user_id == user_id)
        .order_by(WatchlistItem.added_at.desc())
    )
    return list(result.scalars().all())


async def delete_item(
    db: AsyncSession, user_id: str, item_id: int
) -> bool:
    """Remove an item from the watchlist."""
    result = await db.execute(
        select(WatchlistItem).where(
            WatchlistItem.id == item_id,
            WatchlistItem.user_id == user_id,
        )
    )
    item = result.scalars().first()
    if item is None:
        return False
    await db.delete(item)
    await db.flush()
    return True


async def refresh_prices(
    db: AsyncSession, user_id: str
) -> list[WatchlistItem]:
    """Refresh prices for all watchlist items."""
    items = await get_items(db, user_id)
    for i, item in enumerate(items):
        if i > 0:
            await asyncio.sleep(1.5)
        try:
            quote = await market_data.get_quote(item.ticker)
            if quote["price"] is not None:
                item.last_price = quote["price"]
            if quote["previous_close"] is not None:
                item.previous_close = quote["previous_close"]
            db.add(item)
        except Exception as exc:
            logger.warning("Price refresh failed for %s: %s", item.ticker, exc)

    await db.flush()
    for item in items:
        await db.refresh(item)
    return items
