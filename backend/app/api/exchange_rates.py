from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import date, timedelta

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.rates import ExchangeRate
from app.schemas.rates import ExchangeRateResponse, ExchangeRateListResponse
from app.services.frankfurter_client import frankfurter_client

router = APIRouter(prefix="/api/exchange-rates", tags=["exchange-rates"])


@router.get("/latest", response_model=ExchangeRateListResponse)
async def get_latest_rates(
    base: str = Query(default="USD"),
    quotes: str = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quotes_list = quotes.split(",") if quotes else None

    cached_rates = await db.execute(
        select(ExchangeRate)
        .where(ExchangeRate.date == date.today())
        .where(ExchangeRate.base_currency == base)
    )
    cached_rates = cached_rates.scalars().all()

    if cached_rates:
        rates = [
            ExchangeRateResponse.from_orm(rate)
            for rate in cached_rates
            if not quotes_list or rate.target_currency in quotes_list
        ]
        return ExchangeRateListResponse(rates=rates, count=len(rates))

    external_data = await frankfurter_client.get_latest_rates(
        base=base, quotes=quotes_list
    )

    rates = []
    if external_data and "rates" in external_data:
        for target, rate_value in external_data["rates"].items():
            exchange_rate = ExchangeRate(
                base_currency=base,
                target_currency=target,
                rate=rate_value,
                date=date.today(),
            )
            db.add(exchange_rate)
            rates.append(ExchangeRateResponse.from_orm(exchange_rate))

        await db.commit()

    return ExchangeRateListResponse(rates=rates, count=len(rates))


@router.get("/historical", response_model=ExchangeRateListResponse)
async def get_historical_rates(
    base: str = Query(default="USD"),
    quotes: str = Query(...),
    from_date: date = Query(...),
    to_date: date = Query(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    quotes_list = quotes.split(",")

    cached_rates = await db.execute(
        select(ExchangeRate)
        .where(ExchangeRate.date >= from_date)
        .where(ExchangeRate.date <= to_date)
        .where(ExchangeRate.base_currency == base)
        .where(ExchangeRate.target_currency.in_(quotes_list))
    )
    cached_rates = cached_rates.scalars().all()

    if cached_rates:
        rates = [ExchangeRateResponse.from_orm(rate) for rate in cached_rates]
        return ExchangeRateListResponse(rates=rates, count=len(rates))

    external_data = await frankfurter_client.get_historical_rates(
        base=base, quotes=quotes_list, from_date=from_date, to_date=to_date
    )

    rates = []
    if external_data:
        for rate_data in external_data:
            for target, rate_value in rate_data.get("rates", {}).items():
                exchange_rate = ExchangeRate(
                    base_currency=base,
                    target_currency=target,
                    rate=rate_value,
                    date=rate_data.get("date"),
                    source="frankfurter",
                )
                db.add(exchange_rate)
                rates.append(ExchangeRateResponse.from_orm(exchange_rate))

        await db.commit()

    return ExchangeRateListResponse(rates=rates, count=len(rates))


@router.get("/currencies")
async def get_supported_currencies():
    currencies = await frankfurter_client.get_supported_currencies()
    return {"currencies": currencies}
