from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .holding import HoldingRead


class PortfolioCreate(BaseModel):
    name: str


class PortfolioUpdate(BaseModel):
    name: str | None = None


class PortfolioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    created_at: datetime
    updated_at: datetime


class PortfolioDetail(PortfolioRead):
    """Portfolio with nested holdings list."""

    holdings: list[HoldingRead] = []
