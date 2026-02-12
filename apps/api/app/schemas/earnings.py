from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class EarningsCallRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    holding_id: int | None = None
    call_date: datetime | None = None
    summary: str | None = None
    key_metrics: dict | None = None
    sentiment_score: float | None = None
    risk_mentions: int | None = None
    growth_mentions: int | None = None
    guidance_outlook: str | None = None
    created_at: datetime


class EarningsAnalyzeRequest(BaseModel):
    """Request body for triggering earnings analysis."""

    transcript: str | None = Field(None, max_length=100000)  # If user provides transcript directly
