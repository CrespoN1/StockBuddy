"""
Billing & subscription management endpoints.
"""

import stripe
import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.config import settings
from app.database import get_db
from app.models import Portfolio
from app.schemas.subscription import (
    BillingPortalResponse,
    CheckoutSessionResponse,
    SubscriptionRead,
    UsageInfo,
)
from app.services import subscription as sub_svc

logger = structlog.stdlib.get_logger(__name__)

router = APIRouter(prefix="/billing", tags=["billing"])


@router.get("/subscription", response_model=SubscriptionRead)
async def get_subscription(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Get the current user's subscription details and usage."""
    sub = await sub_svc.get_or_create_subscription(db, user_id)
    limits = sub_svc.get_limits(sub.plan)

    return SubscriptionRead(
        plan=sub.plan,
        status=sub.status,
        current_period_end=sub.current_period_end,
        cancel_at_period_end=sub.cancel_at_period_end,
        earnings_analysis_count=sub.earnings_analysis_count,
        portfolio_analysis_count=sub.portfolio_analysis_count,
        earnings_analysis_limit=limits["earnings_analysis_per_month"],
        portfolio_analysis_limit=limits["portfolio_analysis_per_month"],
        portfolio_limit=limits["portfolios"],
        holdings_per_portfolio_limit=limits["holdings_per_portfolio"],
    )


@router.get("/usage", response_model=UsageInfo)
async def get_usage(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Get detailed usage info with boolean can_* flags."""
    sub = await sub_svc.get_or_create_subscription(db, user_id)
    limits = sub_svc.get_limits(sub.plan)

    count_result = await db.execute(
        select(func.count(Portfolio.id)).where(Portfolio.user_id == user_id)
    )
    portfolio_count = count_result.scalar() or 0

    return UsageInfo(
        plan=sub.plan,
        earnings_analysis_used=sub.earnings_analysis_count,
        earnings_analysis_limit=limits["earnings_analysis_per_month"],
        portfolio_analysis_used=sub.portfolio_analysis_count,
        portfolio_analysis_limit=limits["portfolio_analysis_per_month"],
        portfolio_count=portfolio_count,
        portfolio_limit=limits["portfolios"],
        can_create_portfolio=(
            limits["portfolios"] is None or portfolio_count < limits["portfolios"]
        ),
        can_analyze_earnings=(
            limits["earnings_analysis_per_month"] is None
            or sub.earnings_analysis_count < limits["earnings_analysis_per_month"]
        ),
        can_analyze_portfolio=(
            limits["portfolio_analysis_per_month"] is None
            or sub.portfolio_analysis_count < limits["portfolio_analysis_per_month"]
        ),
        can_compare=limits["can_compare"],
        can_forecast=limits["can_forecast"],
        can_export_csv=limits["can_export_csv"],
    )


@router.post("/checkout", response_model=CheckoutSessionResponse)
async def create_checkout(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Create a Stripe Checkout session for Pro upgrade."""
    if not settings.stripe_secret_key:
        raise HTTPException(503, "Stripe is not configured")

    success_url = f"{settings.cors_origin_list[0]}/billing?session_id={{CHECKOUT_SESSION_ID}}"
    cancel_url = f"{settings.cors_origin_list[0]}/billing"

    url = await sub_svc.create_checkout_session(db, user_id, success_url, cancel_url)
    return CheckoutSessionResponse(checkout_url=url)


@router.post("/portal", response_model=BillingPortalResponse)
async def create_portal(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    """Create a Stripe Billing Portal session for managing subscription."""
    if not settings.stripe_secret_key:
        raise HTTPException(503, "Stripe is not configured")

    return_url = f"{settings.cors_origin_list[0]}/billing"

    try:
        url = await sub_svc.create_billing_portal_session(db, user_id, return_url)
    except ValueError:
        raise HTTPException(400, "No active subscription found")

    return BillingPortalResponse(portal_url=url)


@router.post("/webhook", include_in_schema=False)
async def stripe_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle Stripe webhook events. This endpoint is UNAUTHENTICATED."""
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature", "")

    if not settings.stripe_webhook_secret:
        raise HTTPException(503, "Webhook secret not configured")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.stripe_webhook_secret
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(400, "Invalid webhook signature")

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        await sub_svc.handle_checkout_completed(db, data)
    elif event_type == "customer.subscription.updated":
        await sub_svc.handle_subscription_updated(db, data)
    elif event_type == "customer.subscription.deleted":
        await sub_svc.handle_subscription_deleted(db, data)
    else:
        logger.debug("Unhandled Stripe event", event_type=event_type)

    return {"status": "ok"}
