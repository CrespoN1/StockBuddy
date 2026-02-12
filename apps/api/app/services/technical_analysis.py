"""
Technical analysis indicators.

Migrated from: main.py _run_technical_analysis_thread() (lines 516-603)
Changes: extracted pure calculation logic from GUI thread, returns structured data.
"""

import asyncio
import logging

import pandas as pd
import yfinance as yf

from app.schemas.stock import TechnicalIndicators

logger = logging.getLogger(__name__)


def _compute_technicals_sync(ticker: str) -> dict | None:
    """Blocking computation — intended to run via asyncio.to_thread."""
    try:
        stock = yf.Ticker(ticker)
        df: pd.DataFrame = stock.history(period="1y")

        if df is None or df.empty:
            return None

        current_price = float(df["Close"].iloc[-1])

        # Moving averages
        ma20 = df["Close"].rolling(window=20).mean().iloc[-1]
        ma50 = df["Close"].rolling(window=50).mean().iloc[-1]
        ma200 = df["Close"].rolling(window=200).mean().iloc[-1]

        # RSI (14-day)
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi_raw = rs.iloc[-1]
        rsi = 100 - (100 / (1 + rsi_raw)) if not pd.isna(rsi_raw) else 50.0

        if rsi > 70:
            rsi_signal = "Overbought"
        elif rsi < 30:
            rsi_signal = "Oversold"
        else:
            rsi_signal = "Neutral"

        # Volume
        avg_volume = float(df["Volume"].mean())
        current_volume = float(df["Volume"].iloc[-1])
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0

        # Support / resistance (20-day range)
        support = float(df["Low"].tail(20).min())
        resistance = float(df["High"].tail(20).max())

        return {
            "ticker": ticker.upper(),
            "current_price": round(current_price, 2),
            "ma_20": round(float(ma20), 2) if not pd.isna(ma20) else None,
            "ma_50": round(float(ma50), 2) if not pd.isna(ma50) else None,
            "ma_200": round(float(ma200), 2) if not pd.isna(ma200) else None,
            "rsi_14": round(float(rsi), 1),
            "rsi_signal": rsi_signal,
            "current_volume": round(current_volume, 0),
            "avg_volume": round(avg_volume, 0),
            "volume_ratio": round(volume_ratio, 1),
            "support": round(support, 2),
            "resistance": round(resistance, 2),
        }
    except Exception as exc:
        logger.error("Technical analysis error for %s: %s", ticker, exc)
        return None


async def get_technical_indicators(ticker: str) -> TechnicalIndicators | None:
    raw = await asyncio.to_thread(_compute_technicals_sync, ticker)
    if raw is None:
        return None
    return TechnicalIndicators(**raw)
