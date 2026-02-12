"""
Stock price forecasting using linear regression + moving averages.

Uses historical price data from yfinance to build a simple predictive
model that forecasts future stock prices.
"""

import asyncio
import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class ForecastError(Exception):
    pass


def _build_forecast_sync(ticker: str, forecast_days: int = 30) -> dict:
    """Build a price forecast — blocking call, run via asyncio.to_thread.

    Uses:
    1. Linear regression on closing prices for trend
    2. 20-day and 50-day moving averages for mean reversion signal
    3. Bollinger Bands for confidence intervals
    4. RSI for momentum signal

    Returns dict with forecast data.
    """
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="1y")

        if df is None or df.empty or len(df) < 60:
            return {"error": f"Insufficient data for {ticker} (need at least 60 days)"}

        close = df["Close"].values
        dates = np.arange(len(close))

        # --- Linear Regression (trend) ---
        # Fit line to last 6 months for recent trend
        recent_n = min(126, len(close))  # ~6 months of trading days
        recent_close = close[-recent_n:]
        recent_dates = np.arange(recent_n)

        coeffs = np.polyfit(recent_dates, recent_close, 1)
        slope = coeffs[0]
        intercept = coeffs[1]

        # --- Moving Averages ---
        ma_20 = pd.Series(close).rolling(20).mean().iloc[-1]
        ma_50 = pd.Series(close).rolling(50).mean().iloc[-1]

        # --- Bollinger Bands (20-day) ---
        bb_std = pd.Series(close).rolling(20).std().iloc[-1]
        bb_upper = ma_20 + 2 * bb_std
        bb_lower = ma_20 - 2 * bb_std

        # --- RSI (14-day) ---
        delta = pd.Series(close).diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
        rs = gain / loss if loss > 0 else 100
        rsi = 100 - (100 / (1 + rs))

        # --- Momentum signal ---
        momentum_factor = 1.0
        if rsi > 70:
            momentum_factor = 0.95  # Overbought: reduce upside prediction
        elif rsi < 30:
            momentum_factor = 1.05  # Oversold: increase upside prediction

        # --- Mean reversion signal ---
        current_price = close[-1]
        ma_factor = 1.0
        if current_price > ma_50 * 1.1:
            ma_factor = 0.98  # Far above MA50: slight pullback expected
        elif current_price < ma_50 * 0.9:
            ma_factor = 1.02  # Far below MA50: slight rebound expected

        # --- Generate forecast ---
        forecast_dates = []
        forecast_prices = []
        upper_bound = []
        lower_bound = []

        last_date = df.index[-1].to_pydatetime()

        for i in range(1, forecast_days + 1):
            future_x = recent_n + i
            base_price = slope * future_x + intercept

            # Apply momentum and mean reversion adjustments
            adjusted_price = base_price * momentum_factor * ma_factor

            # Confidence interval widens over time
            uncertainty = bb_std * np.sqrt(i / 20)
            upper = adjusted_price + 2 * uncertainty
            lower = adjusted_price - 2 * uncertainty

            forecast_date = last_date + timedelta(days=i)
            forecast_dates.append(forecast_date.strftime("%Y-%m-%d"))
            forecast_prices.append(round(float(adjusted_price), 2))
            upper_bound.append(round(float(upper), 2))
            lower_bound.append(round(float(max(lower, 0)), 2))

        # --- Historical prices (last 90 days for chart context) ---
        hist_dates = []
        hist_prices = []
        for ts, row in df.tail(90).iterrows():
            hist_dates.append(ts.strftime("%Y-%m-%d"))
            hist_prices.append(round(float(row["Close"]), 2))

        # --- Summary statistics ---
        forecast_end_price = forecast_prices[-1]
        price_change = forecast_end_price - current_price
        pct_change = (price_change / current_price) * 100 if current_price > 0 else 0.0

        if pct_change > 5:
            trend_signal = "Bullish"
        elif pct_change < -5:
            trend_signal = "Bearish"
        else:
            trend_signal = "Neutral"

        return {
            "ticker": ticker.upper(),
            "current_price": round(float(current_price), 2),
            "forecast_days": forecast_days,
            "trend_signal": trend_signal,
            "predicted_price": forecast_end_price,
            "price_change": round(float(price_change), 2),
            "pct_change": round(float(pct_change), 2),
            "rsi": round(float(rsi), 1),
            "ma_20": round(float(ma_20), 2),
            "ma_50": round(float(ma_50), 2),
            "historical": {
                "dates": hist_dates,
                "prices": hist_prices,
            },
            "forecast": {
                "dates": forecast_dates,
                "prices": forecast_prices,
                "upper_bound": upper_bound,
                "lower_bound": lower_bound,
            },
            "model_info": {
                "method": "Linear Regression + MA + RSI + Bollinger Bands",
                "training_period": f"{recent_n} trading days",
                "slope_per_day": round(float(slope), 4),
                "r_squared": round(float(
                    1 - np.sum((recent_close - np.polyval(coeffs, recent_dates)) ** 2)
                    / np.sum((recent_close - np.mean(recent_close)) ** 2)
                ), 4),
            },
        }

    except Exception as exc:
        logger.error("Forecast error for %s: %s", ticker, exc)
        return {"error": f"Failed to generate forecast for {ticker}: {str(exc)}"}


async def get_forecast(ticker: str, forecast_days: int = 30) -> dict:
    """Async wrapper for forecast generation."""
    return await asyncio.to_thread(_build_forecast_sync, ticker, forecast_days)
