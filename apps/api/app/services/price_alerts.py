"""Price alert CRUD and checking logic."""

import structlog
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.price_alert import PriceAlert
from app.schemas.price_alert import AlertsSummary

logger = structlog.stdlib.get_logger(__name__)


async def create_alert(
    db: AsyncSession,
    user_id: str,
    ticker: str,
    target_price: float,
    direction: str,
) -> PriceAlert:
    alert = PriceAlert(
        user_id=user_id,
        ticker=ticker.upper(),
        target_price=target_price,
        direction=direction,
    )
    db.add(alert)
    await db.flush()
    await db.refresh(alert)
    return alert


async def get_alerts(db: AsyncSession, user_id: str) -> list[PriceAlert]:
    result = await db.execute(
        select(PriceAlert)
        .where(PriceAlert.user_id == user_id)
        .order_by(PriceAlert.created_at.desc())
    )
    return list(result.scalars().all())


async def get_alert_counts(db: AsyncSession, user_id: str) -> AlertsSummary:
    active_result = await db.execute(
        select(func.count())
        .select_from(PriceAlert)
        .where(PriceAlert.user_id == user_id, PriceAlert.triggered == False)  # noqa: E712
    )
    triggered_result = await db.execute(
        select(func.count())
        .select_from(PriceAlert)
        .where(PriceAlert.user_id == user_id, PriceAlert.triggered == True)  # noqa: E712
    )
    return AlertsSummary(
        active_count=active_result.scalar() or 0,
        triggered_count=triggered_result.scalar() or 0,
    )


async def delete_alert(db: AsyncSession, user_id: str, alert_id: int) -> bool:
    result = await db.execute(
        select(PriceAlert).where(
            PriceAlert.id == alert_id,
            PriceAlert.user_id == user_id,
        )
    )
    alert = result.scalars().first()
    if alert is None:
        return False
    await db.delete(alert)
    await db.flush()
    return True


async def check_alerts_for_ticker(
    db: AsyncSession, ticker: str, current_price: float
) -> None:
    """Check and trigger any active alerts for the given ticker."""
    result = await db.execute(
        select(PriceAlert).where(
            PriceAlert.ticker == ticker.upper(),
            PriceAlert.triggered == False,  # noqa: E712
        )
    )
    alerts = list(result.scalars().all())

    for alert in alerts:
        should_trigger = (
            (alert.direction == "above" and current_price >= alert.target_price)
            or (alert.direction == "below" and current_price <= alert.target_price)
        )
        if should_trigger:
            alert.triggered = True
            alert.triggered_at = datetime.now(timezone.utc)
            alert.triggered_price = current_price
            db.add(alert)
            logger.info(
                "Price alert triggered",
                alert_id=alert.id,
                ticker=alert.ticker,
                direction=alert.direction,
                target=alert.target_price,
                current=current_price,
            )

    if alerts:
        await db.flush()
