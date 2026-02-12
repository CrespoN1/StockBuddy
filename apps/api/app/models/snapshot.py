from datetime import datetime, timezone
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .portfolio import Portfolio


class PortfolioSnapshot(SQLModel, table=True):
    """Point-in-time snapshot of portfolio analysis metrics."""

    __tablename__ = "portfolio_snapshot"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    portfolio_id: int = Field(foreign_key="portfolio.id", index=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sa.DateTime(timezone=True),
    )

    # Financial metrics
    total_value: float | None = None
    num_positions: int = 0

    # Earnings-based metrics
    recent_earnings_coverage: float | None = None
    avg_sentiment_score: float | None = None
    risk_exposure_score: float | None = None

    # Health metrics
    health_score: int | None = None
    concentration_risk: float | None = None

    portfolio: "Portfolio" = Relationship(back_populates="snapshots")
