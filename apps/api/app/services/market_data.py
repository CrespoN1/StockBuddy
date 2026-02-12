"""
Async Alpha Vantage integration.

Migrated from: market_data.py (original StockBuddy)
Changes: sync httpx → async httpx, added retry logic, proper error handling.
"""

import structlog

import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import settings

logger = structlog.stdlib.get_logger(__name__)


class MarketDataError(Exception):
    pass


def _require_api_key() -> None:
    if not settings.alpha_vantage_api_key:
        raise MarketDataError("Missing ALPHA_VANTAGE_API_KEY in environment.")


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def get_stock_fundamentals(ticker: str) -> dict:
    """
    Fetch stock overview and upcoming earnings date from Alpha Vantage.

    Returns dict with keys: price, currency, sector, beta, dividend_yield,
    next_earnings_date, market_cap, pe_ratio.
    """
    _require_api_key()
    ticker = ticker.upper()

    result: dict = {
        "price": None,
        "currency": "USD",
        "sector": None,
        "beta": None,
        "dividend_yield": None,
        "next_earnings_date": None,
        "market_cap": None,
        "pe_ratio": None,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        # --- Company overview ---
        overview_resp = await client.get(
            settings.alpha_vantage_base_url,
            params={
                "function": "OVERVIEW",
                "symbol": ticker,
                "apikey": settings.alpha_vantage_api_key,
            },
        )

        if overview_resp.status_code == 200:
            data = overview_resp.json()
            result["sector"] = data.get("Sector") or None
            result["market_cap"] = data.get("MarketCapitalization") or None
            result["pe_ratio"] = data.get("PERatio") or None

            for key, field in [("Beta", "beta"), ("DividendYield", "dividend_yield")]:
                raw = data.get(key)
                if raw not in (None, "", "None"):
                    try:
                        result[field] = float(raw)
                    except (ValueError, TypeError):
                        pass

        # --- Earnings calendar ---
        try:
            earnings_resp = await client.get(
                settings.alpha_vantage_base_url,
                params={
                    "function": "EARNINGS_CALENDAR",
                    "symbol": ticker,
                    "horizon": "3month",
                    "apikey": settings.alpha_vantage_api_key,
                },
            )
            if earnings_resp.status_code == 200:
                earnings_data = earnings_resp.json()
                if isinstance(earnings_data, dict) and "earningsCalendar" in earnings_data:
                    cal = earnings_data["earningsCalendar"]
                    if cal:
                        result["next_earnings_date"] = cal[0].get("reportDate")
        except (httpx.HTTPError, KeyError, IndexError) as exc:
            logger.warning("Failed to fetch earnings calendar for %s: %s", ticker, exc)

    return result


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
async def get_latest_price(ticker: str) -> float | None:
    """Fetch the latest price via GLOBAL_QUOTE."""
    _require_api_key()

    async with httpx.AsyncClient(timeout=5.0) as client:
        resp = await client.get(
            settings.alpha_vantage_base_url,
            params={
                "function": "GLOBAL_QUOTE",
                "symbol": ticker.upper(),
                "apikey": settings.alpha_vantage_api_key,
            },
        )
        if resp.status_code == 200:
            data = resp.json()
            try:
                return float(data["Global Quote"]["05. price"])
            except (KeyError, ValueError, TypeError):
                logger.warning("Could not parse price for %s", ticker)
                return None
    return None
