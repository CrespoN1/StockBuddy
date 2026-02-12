from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .holding import Holding


class EarningsCall(SQLModel, table=True):
    """Analyzed earnings call transcript for a stock."""

    __tablename__ = "earnings_call"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    holding_id: int | None = Field(default=None, foreign_key="holding.id", index=True)
    ticker: str = Field(index=True)

    call_date: datetime | None = None
    extracted_text: str | None = Field(default=None, sa_column=Column(Text))
    summary: str | None = Field(default=None, sa_column=Column(Text))
    key_metrics: dict | None = Field(default=None, sa_column=Column(JSONB))

    # Analysis results
    sentiment_score: float | None = None
    risk_mentions: int | None = None
    growth_mentions: int | None = None
    guidance_outlook: str | None = None  # "positive", "neutral", "negative"

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    holding: "Holding" = Relationship(back_populates="earnings_calls")
