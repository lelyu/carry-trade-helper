from fastapi import APIRouter, Depends, Query, HTTPException
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
):
    quotes_list = quotes.split(",") if quotes else None

    try:
        external_data = await frankfurter_client.get_latest_rates(
            base=base, quotes=quotes_list
        )
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Error fetching exchange rates: {str(e)}"
        )

    if not external_data:
        return ExchangeRateListResponse(rates=[], count=0)

    dates = {item["date"] for item in external_data}
    target_currencies = [item["quote"] for item in external_data]

    existing_rates = await db.execute(
        select(ExchangeRate)
        .where(ExchangeRate.date.in_(dates))
        .where(ExchangeRate.base_currency == base)
        .where(ExchangeRate.target_currency.in_(target_currencies))
    )
    existing_rates = existing_rates.scalars().all()

    existing_set = {
        (r.base_currency, r.target_currency, r.date) for r in existing_rates
    }

    rates = []
    exchange_rates = []

    for item in external_data:
        if quotes_list and item["quote"] not in quotes_list:
            continue

        key = (item["base"], item["quote"], item["date"])

        if key in existing_set:
            existing = next(
                r
                for r in existing_rates
                if r.base_currency == item["base"]
                and r.target_currency == item["quote"]
                and r.date == item["date"]
            )
            rates.append(ExchangeRateResponse.model_validate(existing))
        else:
            exchange_rate = ExchangeRate(
                base_currency=item["base"],
                target_currency=item["quote"],
                rate=item["rate"],
                date=item["date"],
            )
            db.add(exchange_rate)
            exchange_rates.append(exchange_rate)

    if exchange_rates:
        await db.commit()
        for exchange_rate in exchange_rates:
            await db.refresh(exchange_rate)
            rates.append(ExchangeRateResponse.model_validate(exchange_rate))

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

    try:
        external_data = await frankfurter_client.get_historical_rates(
            base=base, quotes=quotes_list, from_date=from_date, to_date=to_date
        )
    except Exception as e:
        raise HTTPException(
            status_code=502, detail=f"Error fetching historical rates: {str(e)}"
        )

    if not external_data:
        return ExchangeRateListResponse(rates=[], count=0)

    dates = {item["date"] for item in external_data}
    target_currencies = [item["quote"] for item in external_data]

    existing_rates = await db.execute(
        select(ExchangeRate)
        .where(ExchangeRate.date.in_(dates))
        .where(ExchangeRate.base_currency == base)
        .where(ExchangeRate.target_currency.in_(target_currencies))
    )
    existing_rates = existing_rates.scalars().all()

    existing_set = {
        (r.base_currency, r.target_currency, r.date) for r in existing_rates
    }

    rates = []
    exchange_rates = []

    for item in external_data:
        key = (item["base"], item["quote"], item["date"])

        if key in existing_set:
            existing = next(
                r
                for r in existing_rates
                if r.base_currency == item["base"]
                and r.target_currency == item["quote"]
                and r.date == item["date"]
            )
            rates.append(ExchangeRateResponse.model_validate(existing))
        else:
            exchange_rate = ExchangeRate(
                base_currency=item["base"],
                target_currency=item["quote"],
                rate=item["rate"],
                date=item["date"],
                source="frankfurter",
            )
            db.add(exchange_rate)
            exchange_rates.append(exchange_rate)

    if exchange_rates:
        await db.commit()
        for exchange_rate in exchange_rates:
            await db.refresh(exchange_rate)
            rates.append(ExchangeRateResponse.model_validate(exchange_rate))

    return ExchangeRateListResponse(rates=rates, count=len(rates))


@router.get("/currencies")
async def get_supported_currencies():
    currencies = await frankfurter_client.get_supported_currencies()
    return {"currencies": currencies}
