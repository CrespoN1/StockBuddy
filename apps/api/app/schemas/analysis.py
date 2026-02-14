from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PortfolioSnapshotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    portfolio_id: int
    created_at: datetime
    total_value: float | None = None
    num_positions: int = 0
    recent_earnings_coverage: float | None = None
    avg_sentiment_score: float | None = None
    risk_exposure_score: float | None = None
    health_score: int | None = None
    concentration_risk: float | None = None
    daily_change: float | None = None
    daily_change_pct: float | None = None


class SectorAllocation(BaseModel):
    sector: str
    weight: float  # 0.0 – 1.0
    value: float


class EarningsInsights(BaseModel):
    holdings_with_recent_earnings: list[str] = []
    positive_outlooks: list[str] = []
    risk_warnings: list[str] = []
    recommended_reviews: list[str] = []
    sentiment_summary: dict[str, int] = {}


class JobStatus(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    job_type: str
    status: str  # pending, processing, completed, failed
    input_data: dict | None = None
    result: dict | None = None
    error: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class CompareRequest(BaseModel):
    tickers: list[str] = Field(..., min_length=2, max_length=5)


class PerformerInfo(BaseModel):
    ticker: str
    daily_change_pct: float


class DashboardSummary(BaseModel):
    best_performer: PerformerInfo | None = None
    worst_performer: PerformerInfo | None = None
    upcoming_earnings_count: int = 0
    upcoming_earnings_tickers: list[str] = []
