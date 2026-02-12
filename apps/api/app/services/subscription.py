"""
Subscription management and tier enforcement.

Handles Stripe customer creation, checkout sessions, billing portal,
webhook processing, and usage limit checking.
"""

import stripe
import structlog
from datetime import datetime, timezone, timedelta
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.models import Portfolio, Subscription

logger = structlog.stdlib.get_logger(__name__)

# ─── Plan limits ─────────────────────────────────────────────────────

FREE_LIMITS = {
    "portfolios": 1,
    "holdings_per_portfolio": 10,
    "earnings_analysis_per_month": 3,
    "portfolio_analysis_per_month": 1,
    "can_compare": False,
    "can_forecast": False,
    "can_export_csv": False,
    "show_sentiment_scores": False,
}

PRO_LIMITS = {
    "portfolios": None,  # unlimited
    "holdings_per_portfolio": None,
    "earnings_analysis_per_month": None,
    "portfolio_analysis_per_month": None,
    "can_compare": True,
    "can_forecast": True,
    "can_export_csv": True,
    "show_sentiment_scores": True,
}


def get_limits(plan: str) -> dict:
    """Return the limits dict for a given plan."""
    return PRO_LIMITS if plan == "pro" else FREE_LIMITS


def _init_stripe():
    """Set the Stripe API key from settings."""
    stripe.api_key = settings.stripe_secret_key


# ─── Subscription CRUD ───────────────────────────────────────────────


async def get_or_create_subscription(
    db: AsyncSession, user_id: str
) -> Subscription:
    """Get existing subscription or create a free-tier default."""
    result = await db.execute(
        select(Subscription).where(Subscription.user_id == user_id)
    )
    sub = result.scalars().first()
    if sub is not None:
        await _maybe_reset_usage(db, sub)
        return sub

    sub = Subscription(user_id=user_id)
    db.add(sub)
    await db.flush()
    await db.refresh(sub)
    return sub


async def _maybe_reset_usage(db: AsyncSession, sub: Subscription) -> None:
    """Reset monthly usage counters if a month has passed."""
    now = datetime.now(timezone.utc)
    # Ensure usage_reset_at is timezone-aware (SQLite strips tzinfo)
    reset_at = sub.usage_reset_at
    if reset_at.tzinfo is None:
        reset_at = reset_at.replace(tzinfo=timezone.utc)
    if now - reset_at > timedelta(days=30):
        sub.earnings_analysis_count = 0
        sub.portfolio_analysis_count = 0
        sub.usage_reset_at = now
        sub.updated_at = now
        db.add(sub)
        await db.flush()


# ─── Tier checks ─────────────────────────────────────────────────────


async def check_can_create_portfolio(
    db: AsyncSession, user_id: str
) -> bool:
    """Check if the user can create another portfolio."""
    sub = await get_or_create_subscription(db, user_id)
    limits = get_limits(sub.plan)
    if limits["portfolios"] is None:
        return True
    count_result = await db.execute(
        select(func.count(Portfolio.id)).where(Portfolio.user_id == user_id)
    )
    count = count_result.scalar() or 0
    return count < limits["portfolios"]


async def check_can_add_holding(
    db: AsyncSession, user_id: str, current_count: int
) -> bool:
    """Check if the user can add another holding to a portfolio."""
    sub = await get_or_create_subscription(db, user_id)
    limits = get_limits(sub.plan)
    if limits["holdings_per_portfolio"] is None:
        return True
    return current_count < limits["holdings_per_portfolio"]


async def check_can_analyze_earnings(
    db: AsyncSession, user_id: str
) -> bool:
    """Check if the user has earnings analysis quota remaining."""
    sub = await get_or_create_subscription(db, user_id)
    limits = get_limits(sub.plan)
    if limits["earnings_analysis_per_month"] is None:
        return True
    return sub.earnings_analysis_count < limits["earnings_analysis_per_month"]


async def check_can_analyze_portfolio(
    db: AsyncSession, user_id: str
) -> bool:
    """Check if the user has portfolio analysis quota remaining."""
    sub = await get_or_create_subscription(db, user_id)
    limits = get_limits(sub.plan)
    if limits["portfolio_analysis_per_month"] is None:
        return True
    return sub.portfolio_analysis_count < limits["portfolio_analysis_per_month"]


async def check_can_compare(db: AsyncSession, user_id: str) -> bool:
    """Check if the user has access to comparison feature."""
    sub = await get_or_create_subscription(db, user_id)
    return get_limits(sub.plan)["can_compare"]


async def check_can_forecast(db: AsyncSession, user_id: str) -> bool:
    """Check if the user has access to price forecasting."""
    sub = await get_or_create_subscription(db, user_id)
    return get_limits(sub.plan)["can_forecast"]


async def increment_usage(
    db: AsyncSession, user_id: str, usage_type: str
) -> None:
    """Increment a usage counter after successful analysis."""
    sub = await get_or_create_subscription(db, user_id)
    if usage_type == "earnings_analysis":
        sub.earnings_analysis_count += 1
    elif usage_type == "portfolio_analysis":
        sub.portfolio_analysis_count += 1
    sub.updated_at = datetime.now(timezone.utc)
    db.add(sub)
    await db.flush()


# ─── Stripe operations ───────────────────────────────────────────────


async def create_checkout_session(
    db: AsyncSession, user_id: str, success_url: str, cancel_url: str
) -> str:
    """Create a Stripe Checkout session for Pro upgrade. Returns the checkout URL."""
    _init_stripe()
    sub = await get_or_create_subscription(db, user_id)

    # Ensure Stripe customer exists
    if not sub.stripe_customer_id:
        customer = stripe.Customer.create(metadata={"clerk_user_id": user_id})
        sub.stripe_customer_id = customer.id
        sub.updated_at = datetime.now(timezone.utc)
        db.add(sub)
        await db.flush()

    session = stripe.checkout.Session.create(
        customer=sub.stripe_customer_id,
        mode="subscription",
        line_items=[{"price": settings.stripe_pro_price_id, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"clerk_user_id": user_id},
    )
    return session.url


async def create_billing_portal_session(
    db: AsyncSession, user_id: str, return_url: str
) -> str:
    """Create a Stripe Billing Portal session. Returns the portal URL."""
    _init_stripe()
    sub = await get_or_create_subscription(db, user_id)

    if not sub.stripe_customer_id:
        raise ValueError("No Stripe customer found for this user")

    session = stripe.billing_portal.Session.create(
        customer=sub.stripe_customer_id,
        return_url=return_url,
    )
    return session.url


# ─── Webhook handlers ────────────────────────────────────────────────


async def handle_checkout_completed(
    db: AsyncSession, session_data: dict
) -> None:
    """Handle checkout.session.completed webhook."""
    customer_id = session_data.get("customer")
    subscription_id = session_data.get("subscription")
    user_id = session_data.get("metadata", {}).get("clerk_user_id")

    if not user_id:
        logger.warning("Checkout completed without clerk_user_id metadata")
        return

    sub = await get_or_create_subscription(db, user_id)
    sub.stripe_customer_id = customer_id
    sub.stripe_subscription_id = subscription_id
    sub.plan = "pro"
    sub.status = "active"
    sub.updated_at = datetime.now(timezone.utc)
    db.add(sub)
    await db.commit()
    logger.info("User upgraded to Pro", user_id=user_id)


async def handle_subscription_updated(
    db: AsyncSession, subscription_data: dict
) -> None:
    """Handle customer.subscription.updated webhook."""
    sub_id = subscription_data.get("id")
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == sub_id)
    )
    sub = result.scalars().first()
    if not sub:
        logger.warning("Subscription updated but not found in DB", stripe_sub_id=sub_id)
        return

    status = subscription_data.get("status", "active")
    sub.status = status
    sub.cancel_at_period_end = subscription_data.get("cancel_at_period_end", False)

    period = subscription_data.get("current_period_start")
    if period:
        sub.current_period_start = datetime.fromtimestamp(period, tz=timezone.utc)
    period_end = subscription_data.get("current_period_end")
    if period_end:
        sub.current_period_end = datetime.fromtimestamp(period_end, tz=timezone.utc)

    sub.updated_at = datetime.now(timezone.utc)
    db.add(sub)
    await db.commit()


async def handle_subscription_deleted(
    db: AsyncSession, subscription_data: dict
) -> None:
    """Handle customer.subscription.deleted webhook."""
    sub_id = subscription_data.get("id")
    result = await db.execute(
        select(Subscription).where(Subscription.stripe_subscription_id == sub_id)
    )
    sub = result.scalars().first()
    if not sub:
        return

    sub.plan = "free"
    sub.status = "canceled"
    sub.stripe_subscription_id = None
    sub.updated_at = datetime.now(timezone.utc)
    db.add(sub)
    await db.commit()
    logger.info("User downgraded to Free", user_id=sub.user_id)
