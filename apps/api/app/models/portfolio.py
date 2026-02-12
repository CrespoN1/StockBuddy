from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .holding import Holding
    from .snapshot import PortfolioSnapshot


class Portfolio(SQLModel, table=True):
    """A user's stock portfolio containing multiple holdings."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    holdings: list["Holding"] = Relationship(back_populates="portfolio")
    snapshots: list["PortfolioSnapshot"] = Relationship(back_populates="portfolio")
