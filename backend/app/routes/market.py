from datetime import date

from fastapi import APIRouter, Depends, Query

from app.middleware.auth_middleware import get_current_user
from app.schemas.market_schema import MarketAdvisoryOut, PriceRow, TrendPoint
from app.services import market_service

router = APIRouter(prefix="/market", tags=["Market"], dependencies=[Depends(get_current_user)])


@router.get("/prices", response_model=list[PriceRow])
async def prices(
    crop: str | None = None,
    region: str | None = None,
    market: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    return market_service.get_prices(crop, region, market, start_date, end_date)


@router.get("/trends", response_model=list[TrendPoint])
async def trends(
    crop: str,
    days: int = Query(30, ge=7, le=90),
    market: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    return market_service.get_trends(crop, days, market, start_date, end_date)


@router.get("/advisory", response_model=MarketAdvisoryOut)
async def advisory(crop: str):
    return market_service.get_advisory(crop)
