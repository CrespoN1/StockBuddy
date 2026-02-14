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


def _check_rate_limit(data: dict) -> bool:
    """Return True if the API response indicates a rate limit hit."""
    if "Note" in data or "Information" in data:
        logger.warning("Alpha Vantage rate limit hit: %s", data.get("Note") or data.get("Information"))
        return True
    return False


@retry(stop=stop_after_attempt(2), wait=wait_exponential(min=2, max=10))
async def get_stock_fundamentals(ticker: str) -> dict:
    """
    Fetch stock overview from Alpha Vantage.

    Returns dict with keys: price, currency, sector, beta, dividend_yield,
    next_earnings_date, market_cap, pe_ratio.
    """
    _require_api_key()
    ticker = ticker.upper()

    result: dict = {
        "price": None,
        "currency": "USD",
        "name": None,
        "sector": None,
        "beta": None,
        "dividend_yield": None,
        "next_earnings_date": None,
        "market_cap": None,
        "pe_ratio": None,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
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
            if _check_rate_limit(data):
                return result
            result["name"] = data.get("Name") or None
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

    return result


def _safe_float(val: object) -> float | None:
    """Convert a value to float, returning None on failure."""
    if val is None or val == "" or val == "None":
        return None
    try:
        return float(val)  # type: ignore[arg-type]
    except (ValueError, TypeError):
        return None


@retry(stop=stop_after_attempt(2), wait=wait_exponential(min=2, max=10))
async def get_quote(ticker: str) -> dict:
    """Fetch price and previous close via GLOBAL_QUOTE.

    Returns {"price": float|None, "previous_close": float|None}.
    """
    _require_api_key()
    result = {"price": None, "previous_close": None}

    async with httpx.AsyncClient(timeout=10.0) as client:
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
            if _check_rate_limit(data):
                return result
            gq = data.get("Global Quote", {})
            result["price"] = _safe_float(gq.get("05. price"))
            result["previous_close"] = _safe_float(gq.get("08. previous close"))
    return result


@retry(stop=stop_after_attempt(2), wait=wait_exponential(min=2, max=10))
async def get_latest_price(ticker: str) -> float | None:
    """Fetch the latest price via GLOBAL_QUOTE."""
    quote = await get_quote(ticker)
    return quote["price"]
