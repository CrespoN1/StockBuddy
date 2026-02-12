"""
Ticker search via Massive API.

Migrated from: main.py search_tickers() (lines 665-707)
Changes: sync requests → async httpx, returns structured data instead of populating Tkinter.
"""

import logging

import httpx

from app.config import settings
from app.schemas.stock import StockSearchResult

logger = logging.getLogger(__name__)


async def search_tickers(query: str, limit: int = 20) -> list[StockSearchResult]:
    """Search for stock tickers by name or symbol."""
    if not settings.massive_api_key:
        logger.warning("Missing MASSIVE_API_KEY — search disabled.")
        return []

    params = {"search": query, "limit": limit, "active": True}
    headers = {"Authorization": f"Bearer {settings.massive_api_key}"}

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                settings.massive_base_url,
                params=params,
                headers=headers,
            )

        if resp.status_code != 200:
            logger.warning("Massive API returned %s for query '%s'", resp.status_code, query)
            return []

        data = resp.json()
        results: list[StockSearchResult] = []
        for item in data.get("results", []):
            results.append(
                StockSearchResult(
                    ticker=item.get("ticker", ""),
                    name=item.get("name", "Unknown"),
                )
            )
        return results

    except httpx.HTTPError as exc:
        logger.error("Search request failed: %s", exc)
        return []
