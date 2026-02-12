from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class HoldingCreate(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10, pattern=r"^[A-Za-z.]+$")
    shares: float = Field(..., gt=0)


class HoldingUpdate(BaseModel):
    shares: float = Field(..., gt=0)


class HoldingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    portfolio_id: int
    ticker: str
    shares: float
    last_price: float | None = None
    sector: str | None = None
    beta: float | None = None
    dividend_yield: float | None = None
    latest_earnings_call: datetime | None = None
    earnings_call_summary: str | None = None
    created_at: datetime
    updated_at: datetime

    @property
    def value(self) -> float:
        return (self.last_price or 0.0) * self.shares
