from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SubscriptionRead(BaseModel):
    """Public subscription data returned to frontend."""

    model_config = ConfigDict(from_attributes=True)

    plan: str
    status: str
    current_period_end: datetime | None = None
    cancel_at_period_end: bool = False
    earnings_analysis_count: int = 0
    portfolio_analysis_count: int = 0
    earnings_analysis_limit: int | None = None
    portfolio_analysis_limit: int | None = None
    portfolio_limit: int | None = None
    holdings_per_portfolio_limit: int | None = None


class UsageInfo(BaseModel):
    """Current usage vs limits for the user's plan."""

    plan: str
    earnings_analysis_used: int
    earnings_analysis_limit: int | None
    portfolio_analysis_used: int
    portfolio_analysis_limit: int | None
    portfolio_count: int
    portfolio_limit: int | None
    can_create_portfolio: bool
    can_analyze_earnings: bool
    can_analyze_portfolio: bool
    can_compare: bool
    can_forecast: bool
    can_export_csv: bool


class CheckoutSessionResponse(BaseModel):
    checkout_url: str


class BillingPortalResponse(BaseModel):
    portal_url: str
