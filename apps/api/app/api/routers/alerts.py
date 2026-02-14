from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.database import get_db
from app.schemas.price_alert import PriceAlertCreate, PriceAlertRead, AlertsSummary
from app.services import price_alerts as alert_svc

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.get("", response_model=list[PriceAlertRead])
async def list_alerts(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return await alert_svc.get_alerts(db, user_id)


@router.get("/summary", response_model=AlertsSummary)
async def get_summary(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return await alert_svc.get_alert_counts(db, user_id)


@router.post("", response_model=PriceAlertRead, status_code=201)
async def create_alert(
    body: PriceAlertCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    return await alert_svc.create_alert(
        db, user_id, body.ticker, body.target_price, body.direction
    )


@router.delete("/{alert_id}", status_code=204)
async def delete_alert(
    alert_id: int,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    deleted = await alert_svc.delete_alert(db, user_id, alert_id)
    if not deleted:
        raise HTTPException(404, "Alert not found")
