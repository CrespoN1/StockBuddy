from datetime import datetime, timezone

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class PriceAlert(SQLModel, table=True):
    """User-created price alert for a stock ticker."""

    __tablename__ = "price_alert"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    ticker: str = Field(index=True)
    target_price: float
    direction: str  # "above" or "below"
    triggered: bool = Field(default=False, sa_column_kwargs={"server_default": sa.text("false")})
    triggered_at: datetime | None = Field(
        default=None, sa_type=sa.DateTime(timezone=True)
    )
    triggered_price: float | None = None
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sa.DateTime(timezone=True),
    )
