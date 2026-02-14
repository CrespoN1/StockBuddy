from datetime import datetime

from pydantic import BaseModel


class StockSearchResult(BaseModel):
    ticker: str
    name: str


class StockQuote(BaseModel):
    ticker: str
    price: float | None = None
    currency: str = "USD"


class StockFundamentals(BaseModel):
    ticker: str
    price: float | None = None
    sector: str | None = None
    market_cap: str | None = None
    pe_ratio: str | None = None
    beta: float | None = None
    dividend_yield: float | None = None
    next_earnings_date: str | None = None


class StockInfo(BaseModel):
    """Comprehensive stock details from yfinance."""

    ticker: str
    name: str = ""
    sector: str = "N/A"
    industry: str = "N/A"
    market_cap: str = ""
    pe_ratio: float | str = "N/A"
    forward_pe: float | str = "N/A"
    dividend_yield: float | str = "N/A"
    beta: float | str = "N/A"
    week_52_high: float | str = "N/A"
    week_52_low: float | str = "N/A"
    avg_volume: int | str = "N/A"
    volume: int | str = "N/A"
    employees: int | str = "N/A"
    website: str = "N/A"
    summary: str = ""
    top_institutional: list[dict] | None = None
    latest_recommendation: dict | None = None


class OHLCVBar(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class TechnicalIndicators(BaseModel):
    ticker: str
    current_price: float
    ma_20: float | None = None
    ma_50: float | None = None
    ma_200: float | None = None
    rsi_14: float | None = None
    rsi_signal: str = "Neutral"  # Overbought / Oversold / Neutral
    current_volume: float = 0
    avg_volume: float = 0
    volume_ratio: float = 1.0
    support: float | None = None
    resistance: float | None = None


class NewsArticle(BaseModel):
    title: str
    url: str
    source: str
    published_at: str
    summary: str
    banner_image: str = ""
    overall_sentiment_score: float | None = 0.0
    overall_sentiment_label: str = ""
    ticker_sentiment_score: float | None = 0.0
    ticker_sentiment_label: str = "Neutral"
    ticker_relevance: float | None = 0.0


class ForecastHistorical(BaseModel):
    dates: list[str]
    prices: list[float]


class ForecastPrediction(BaseModel):
    dates: list[str]
    prices: list[float]
    upper_bound: list[float]
    lower_bound: list[float]


class ForecastModelInfo(BaseModel):
    method: str
    training_period: str
    slope_per_day: float
    r_squared: float


class StockForecast(BaseModel):
    ticker: str
    current_price: float
    forecast_days: int
    trend_signal: str
    predicted_price: float
    price_change: float
    pct_change: float
    rsi: float
    ma_20: float
    ma_50: float
    historical: ForecastHistorical
    forecast: ForecastPrediction
    model_info: ForecastModelInfo
