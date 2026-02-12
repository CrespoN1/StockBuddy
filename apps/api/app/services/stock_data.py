"""
Stock info and historical data via yfinance.

Migrated from: stock_chart.py (original StockBuddy)
Changes: removed Tkinter coupling, runs yfinance in thread pool for async compat.
"""

import asyncio
import logging

import pandas as pd
import yfinance as yf

from app.schemas.stock import OHLCVBar, StockInfo

logger = logging.getLogger(__name__)


def _format_market_cap(market_cap: float) -> str:
    """Format market cap to readable string."""
    if not market_cap:
        return ""
    if market_cap >= 1e12:
        return f"${market_cap / 1e12:.2f}T"
    elif market_cap >= 1e9:
        return f"${market_cap / 1e9:.2f}B"
    elif market_cap >= 1e6:
        return f"${market_cap / 1e6:.2f}M"
    return f"${market_cap:,.0f}"


def _fetch_stock_info_sync(ticker: str) -> dict | None:
    """Blocking yfinance call — intended to run via asyncio.to_thread."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        details: dict = {
            "ticker": ticker.upper(),
            "name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": _format_market_cap(info.get("marketCap", 0)),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "forward_pe": info.get("forwardPE", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
            "beta": info.get("beta", "N/A"),
            "week_52_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "week_52_low": info.get("fiftyTwoWeekLow", "N/A"),
            "avg_volume": info.get("averageVolume", "N/A"),
            "volume": info.get("volume", "N/A"),
            "employees": info.get("fullTimeEmployees", "N/A"),
            "website": info.get("website", "N/A"),
            "summary": info.get("longBusinessSummary", ""),
        }

        # Institutional holders
        try:
            inst = stock.institutional_holders
            if inst is not None and not inst.empty:
                details["top_institutional"] = inst.head(5).to_dict("records")
        except Exception:
            pass

        # Latest recommendation
        try:
            recs = stock.recommendations
            if recs is not None and not recs.empty:
                latest = recs.iloc[-1]
                details["latest_recommendation"] = {
                    "firm": latest.get("firm", "N/A"),
                    "rating": latest.get("toGrade", "N/A"),
                    "action": latest.get("action", "N/A"),
                }
        except Exception:
            pass

        return details
    except Exception as exc:
        logger.error("yfinance get_stock_info error for %s: %s", ticker, exc)
        return None


def _fetch_history_sync(ticker: str, period: str = "1y") -> list[dict]:
    """Blocking yfinance history call — intended to run via asyncio.to_thread."""
    try:
        stock = yf.Ticker(ticker)
        df: pd.DataFrame = stock.history(period=period)
        if df is None or df.empty:
            return []

        bars: list[dict] = []
        for ts, row in df.iterrows():
            bars.append(
                {
                    "timestamp": ts.isoformat(),
                    "open": round(row["Open"], 4),
                    "high": round(row["High"], 4),
                    "low": round(row["Low"], 4),
                    "close": round(row["Close"], 4),
                    "volume": int(row["Volume"]),
                }
            )
        return bars
    except Exception as exc:
        logger.error("yfinance history error for %s: %s", ticker, exc)
        return []


# ─── Async public API ────────────────────────────────────────────────

async def get_stock_info(ticker: str) -> StockInfo | None:
    raw = await asyncio.to_thread(_fetch_stock_info_sync, ticker)
    if raw is None:
        return None
    return StockInfo(**raw)


async def get_stock_history(ticker: str, period: str = "1y") -> list[OHLCVBar]:
    bars = await asyncio.to_thread(_fetch_history_sync, ticker, period)
    return [OHLCVBar(**b) for b in bars]
