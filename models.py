# models.py
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


class EarningsCall(SQLModel, table=True):
    """Store analyzed earnings calls for historical reference"""
    id: Optional[int] = Field(default=None, primary_key=True)
    ticker: str = Field(index=True)
    call_date: Optional[datetime] = None
    extracted_text: Optional[str] = None
    summary: Optional[str] = None
    key_metrics: Optional[str] = None  # JSON string of extracted metrics
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Analysis results
    sentiment_score: Optional[float] = None  # -1 to 1
    risk_mentions: Optional[int] = None
    growth_mentions: Optional[int] = None
    guidance_outlook: Optional[str] = None  # "positive", "neutral", "negative"
    portfolio_holding_id: Optional[int] = None  # Just a reference, not a foreign key


class EnhancedHolding(SQLModel, table=True):
    """Extended holding model with earnings call linkage"""
    id: Optional[int] = Field(default=None, primary_key=True)
    ticker: str = Field(index=True)
    shares: Optional[float] = None
    portfolio_name: Optional[str] = None

    # Market data
    last_price: Optional[float] = None
    sector: Optional[str] = None
    beta: Optional[float] = None
    dividend_yield: Optional[float] = None

    # Earnings call tracking
    latest_earnings_call: Optional[datetime] = None
    earnings_call_summary: Optional[str] = None


class PortfolioSnapshot(SQLModel, table=True):
    """Portfolio analysis with earnings call insights"""
    id: Optional[int] = Field(default=None, primary_key=True)
    portfolio_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Financial metrics
    total_value: Optional[float] = None
    num_positions: int = 0

    # Earnings-based metrics
    recent_earnings_coverage: Optional[float] = None  # % of holdings with recent earnings analyzed
    avg_sentiment_score: Optional[float] = None
    risk_exposure_score: Optional[float] = None

    # Health metrics
    health_score: Optional[int] = None
    concentration_risk: Optional[float] = None