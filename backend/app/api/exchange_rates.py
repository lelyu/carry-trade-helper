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

# Supported quote currencies (major currencies + commonly traded ones)
# These are currencies with reasonable exchange rates (< 10000) and stable markets
SUPPORTED_CURRENCIES = {
    'USD', 'EUR', 'GBP', 'JPY', 'CHF', 'AUD', 'CAD', 'NZD', 'CNY', 'HKD',
    'SGD', 'SEK', 'NOK', 'DKK', 'KRW', 'MXN', 'INR', 'BRL', 'RUB', 'ZAR',
    'TRY', 'THB', 'TWD', 'AED', 'SAR', 'ILS', 'PLN', 'CZK', 'HUF', 'RON',
    'BGN', 'HRK', 'ISK', 'CLP', 'COP', 'PEN', 'PHP', 'VND', 'IDR', 'MYR'
}


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

    # Filter out unsupported currencies to prevent database overflow errors
    if quotes_list is None:
        external_data = [
            item for item in external_data 
            if item["quote"] in SUPPORTED_CURRENCIES
        ]
    else:
        external_data = [
            item for item in external_data 
            if item["quote"] in quotes_list and item["quote"] in SUPPORTED_CURRENCIES
        ]

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
    base: str = Query(default="USD", max_length=3),
    quotes: str = Query(...),
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
    db: AsyncSession = Depends(get_db),
):
    # 1. Validation: Prevent the 5-year JSON crash
    if (to_date - from_date).days > 366:
        raise HTTPException(
            status_code=400,
            detail="Date range too wide. Please limit requests to 1 year.",
        )

    quotes_list = [q.strip().upper() for q in quotes.split(",")]

    # 2. Filter to supported currencies only
    quotes_list = [q for q in quotes_list if q in SUPPORTED_CURRENCIES]
    
    if not quotes_list:
        return ExchangeRateListResponse(rates=[], count=0)

    # 3. Fetch Data
    try:
        external_data = await frankfurter_client.get_historical_rates(
            base=base, quotes=quotes_list, from_date=from_date, to_date=to_date
        )
    except Exception as e:
        # Log the full error here for debugging
        raise HTTPException(status_code=502, detail="External API unavailable")

    if not external_data:
        return ExchangeRateListResponse(rates=[], count=0)

    # 4. Optimized Database Logic
    # We fetch existing records to avoid duplicates
    dates = {item["date"] for item in external_data}

    stmt = select(ExchangeRate).where(
        ExchangeRate.date.in_(dates),
        ExchangeRate.base_currency == base,
        ExchangeRate.target_currency.in_(quotes_list),
    )
    result = await db.execute(stmt)
    existing_records = result.scalars().all()

    # Create a lookup set for fast O(1) checking
    existing_map = {(r.date, r.target_currency): r for r in existing_records}

    final_rates = []
    to_create = []

    for item in external_data:
        key = (item["date"], item["quote"])

        if key in existing_map:
            # Use existing record
            final_rates.append(ExchangeRateResponse.model_validate(existing_map[key]))
        else:
            # Prepare new record
            new_rate = ExchangeRate(
                base_currency=item["base"],
                target_currency=item["quote"],
                rate=item["rate"],
                date=item["date"],
                source="frankfurter",
            )
            to_create.append(new_rate)
            # Add to response immediately without waiting for DB ID
            final_rates.append(ExchangeRateResponse.model_validate(new_rate))

    # 4. Batch Insert (Much faster than individual adds)
    if to_create:
        db.add_all(to_create)
        try:
            await db.commit()
            # Note: We skip db.refresh() here to save speed.
            # If you need the DB-generated IDs in the response,
            # you must refresh, but usually, the data itself is enough.
        except Exception:
            await db.rollback()

    return ExchangeRateListResponse(rates=final_rates, count=len(final_rates))


@router.get("/currencies")
async def get_supported_currencies():
    currencies = await frankfurter_client.get_supported_currencies()
    filtered = {
        c["iso_code"]: c["name"]
        for c in currencies
        if c.get("iso_code") in SUPPORTED_CURRENCIES
    }
    return {"currencies": filtered}
