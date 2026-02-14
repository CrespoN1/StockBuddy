from datetime import datetime, timezone

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class WatchlistItem(SQLModel, table=True):
    """A ticker saved to a user's watchlist with live price data."""

    __tablename__ = "watchlist_item"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    ticker: str = Field(index=True)
    name: str | None = None
    last_price: float | None = None
    previous_close: float | None = None
    sector: str | None = None
    added_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sa.DateTime(timezone=True),
    )
