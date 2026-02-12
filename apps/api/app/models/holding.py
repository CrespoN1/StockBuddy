from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .earnings import EarningsCall
    from .portfolio import Portfolio


class Holding(SQLModel, table=True):
    """A stock holding within a portfolio, with market data and earnings tracking."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    portfolio_id: int = Field(foreign_key="portfolio.id", index=True)
    ticker: str = Field(index=True)
    shares: float = 0.0

    # Market data
    last_price: float | None = None
    sector: str | None = None
    beta: float | None = None
    dividend_yield: float | None = None

    # Earnings tracking
    latest_earnings_call: datetime | None = None
    earnings_call_summary: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    portfolio: "Portfolio" = Relationship(back_populates="holdings")
    earnings_calls: list["EarningsCall"] = Relationship(back_populates="holding")
