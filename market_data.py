# market_data.py
import httpx
from typing import Dict, Optional
from config import ALPHA_VANTAGE_API_KEY, ALPHA_VANTAGE_BASE_URL


class MarketDataError(Exception):
    pass


def _require_api_key():
    if not ALPHA_VANTAGE_API_KEY:
        raise MarketDataError("Missing ALPHA_VANTAGE_API_KEY. Add it to your .env file.")


def get_stock_fundamentals(ticker: str) -> Dict:
    """
    Get comprehensive stock data including earnings dates
    """
    _require_api_key()
    ticker = ticker.upper()

    result = {
        "price": None,
        "currency": "USD",
        "sector": None,
        "beta": None,
        "dividend_yield": None,
        "next_earnings_date": None,
        "last_earnings_date": None,
        "market_cap": None,
        "pe_ratio": None,
    }

    with httpx.Client(timeout=10.0) as client:
        # Get overview
        overview_resp = client.get(
            ALPHA_VANTAGE_BASE_URL,
            params={
                "function": "OVERVIEW",
                "symbol": ticker,
                "apikey": ALPHA_VANTAGE_API_KEY,
            },
        )

        if overview_resp.status_code == 200:
            overview_data = overview_resp.json()

            # Basic info
            result["sector"] = overview_data.get("Sector")
            result["market_cap"] = overview_data.get("MarketCapitalization")
            result["pe_ratio"] = overview_data.get("PERatio")

            # Beta
            beta_val = overview_data.get("Beta")
            if beta_val not in (None, "", "None"):
                try:
                    result["beta"] = float(beta_val)
                except ValueError:
                    pass

            # Dividend yield
            dy_val = overview_data.get("DividendYield")
            if dy_val not in (None, "", "None"):
                try:
                    result["dividend_yield"] = float(dy_val)
                except ValueError:
                    pass

        # Get earnings calendar
        earnings_resp = client.get(
            ALPHA_VANTAGE_BASE_URL,
            params={
                "function": "EARNINGS_CALENDAR",
                "symbol": ticker,
                "horizon": "3month",
                "apikey": ALPHA_VANTAGE_API_KEY,
            },
        )

        if earnings_resp.status_code == 200:
            try:
                earnings_data = earnings_resp.json()
                if isinstance(earnings_data, dict) and "earningsCalendar" in earnings_data:
                    earnings_list = earnings_data["earningsCalendar"]
                    if earnings_list:
                        result["next_earnings_date"] = earnings_list[0].get("reportDate")
            except:
                pass

    return result


def get_latest_price(ticker: str) -> Optional[float]:
    """Get only the latest price"""
    _require_api_key()

    with httpx.Client(timeout=5.0) as client:
        resp = client.get(
            ALPHA_VANTAGE_BASE_URL,
            params={
                "function": "GLOBAL_QUOTE",
                "symbol": ticker.upper(),
                "apikey": ALPHA_VANTAGE_API_KEY,
            },
        )

        if resp.status_code == 200:
            data = resp.json()
            try:
                price_str = data["Global Quote"]["05. price"]
                return float(price_str)
            except Exception:
                return None
    return None