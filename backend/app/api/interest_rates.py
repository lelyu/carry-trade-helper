from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.rates import InterestRate
from app.schemas.rates import InterestRateResponse, InterestRateListResponse
from app.services.fred_client import fred_client
from app.core.config import settings

router = APIRouter(prefix="/api/interest-rates", tags=["interest-rates"])


@router.get("/latest", response_model=InterestRateListResponse)
async def get_latest_rates(
    countries: str = Query(default=None),
    db: AsyncSession = Depends(get_db),
):
    countries_list = (
        countries.split(",")
        if countries
        else ["USA", "EUR", "GBR", "JPN", "CHF", "AUD", "CAD", "NZD"]
    )

    cached_rates = await db.execute(
        select(InterestRate)
        .where(InterestRate.date == date.today())
        .where(InterestRate.country_code.in_(countries_list))
    )
    cached_rates = cached_rates.scalars().all()

    if cached_rates:
        rates = [InterestRateResponse.from_orm(rate) for rate in cached_rates]
        return InterestRateListResponse(rates=rates, count=len(rates))

    external_data = await fred_client.get_interest_rates(country_codes=countries_list)

    rates = []
    for rate_data in external_data:
        interest_rate = InterestRate(
            country_code=rate_data["country_code"],
            currency_code=rate_data["currency_code"],
            rate=rate_data["rate"],
            rate_type=rate_data.get("rate_type", "policy_rate"),
            date=date.today(),
        )
        db.add(interest_rate)
        rates.append(InterestRateResponse.from_orm(interest_rate))

    await db.commit()

    return InterestRateListResponse(rates=rates, count=len(rates))


@router.get("/historical", response_model=InterestRateListResponse)
async def get_historical_rates(
    countries: str = Query(...),
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
):
    countries_list = countries.split(",")

    cached_rates = await db.execute(
        select(InterestRate)
        .where(InterestRate.date >= from_date)
        .where(InterestRate.date <= to_date)
        .where(InterestRate.country_code.in_(countries_list))
    )
    cached_rates = cached_rates.scalars().all()

    if cached_rates:
        rates = [InterestRateResponse.from_orm(rate) for rate in cached_rates]
        return InterestRateListResponse(rates=rates, count=len(rates))

    return InterestRateListResponse(rates=[], count=0)
