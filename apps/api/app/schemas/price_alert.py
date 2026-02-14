from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PriceAlertCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    target_price: float = Field(..., gt=0)
    direction: str = Field(..., pattern=r"^(above|below)$")


class PriceAlertRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    ticker: str
    target_price: float
    direction: str
    triggered: bool
    triggered_at: datetime | None = None
    triggered_price: float | None = None
    created_at: datetime


class AlertsSummary(BaseModel):
    active_count: int = 0
    triggered_count: int = 0
