from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WatchlistItemCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, pattern=r"^[A-Za-z.]+$")


class WatchlistItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticker: str
    name: str | None = None
    last_price: float | None = None
    previous_close: float | None = None
    sector: str | None = None
    added_at: datetime
