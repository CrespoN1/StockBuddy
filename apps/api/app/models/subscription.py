from datetime import datetime, timezone

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


class Subscription(SQLModel, table=True):
    """Tracks a user's Stripe subscription and usage limits."""

    __tablename__ = "subscription"

    id: int | None = Field(default=None, primary_key=True)
    user_id: str = Field(index=True, unique=True)

    # Stripe identifiers
    stripe_customer_id: str | None = Field(default=None, index=True)
    stripe_subscription_id: str | None = Field(default=None, index=True)

    # Plan info
    plan: str = Field(default="free")  # "free" or "pro"
    status: str = Field(default="active")  # "active", "canceled", "past_due", "unpaid"

    # Billing period (for pro users)
    current_period_start: datetime | None = Field(default=None, sa_type=sa.DateTime(timezone=True))
    current_period_end: datetime | None = Field(default=None, sa_type=sa.DateTime(timezone=True))
    cancel_at_period_end: bool = Field(default=False)

    # Usage counters (reset monthly)
    earnings_analysis_count: int = Field(default=0)
    portfolio_analysis_count: int = Field(default=0)
    usage_reset_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sa.DateTime(timezone=True),
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sa.DateTime(timezone=True),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=sa.DateTime(timezone=True),
    )
