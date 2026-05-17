from fastapi import APIRouter, Query, HTTPException
from datetime import date

from app.core.cache import cache
from app.core.config import settings
from app.schemas.rates import (
    ExchangeRateItem,
    ExchangeRateListResponse,
)
from app.services.frankfurter_client import frankfurter_client

router = APIRouter(prefix="/api/exchange-rates", tags=["exchange-rates"])

SUPPORTED_CURRENCIES = {
    "USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD", "CNY", "HKD",
}


def _calc_trend_7d(
    history: dict[str, list[dict]], currency: str, current_rate: float
) -> float | None:
    points = history.get(currency, [])
    if len(points) < 2:
        return None
    sorted_points = sorted(points, key=lambda p: p["date"])
    old_rate = float(sorted_points[0]["rate"])
    if old_rate == 0:
        return None
    change = (current_rate - old_rate) / old_rate * 100
    return round(change, 4)


@router.get("/latest", response_model=ExchangeRateListResponse)
async def get_latest_rates(
    base: str = Query(default="USD", max_length=3),
):
    quotes_list = list(SUPPORTED_CURRENCIES - {base})
    cache_key = f"exchange_latest:{base}"

    async def fetch():
        try:
            data = await frankfurter_client.get_latest_rates(
                base=base, quotes=quotes_list
            )
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"External API unavailable: {str(e)}")

        if not data:
            return {"rates": [], "as_of": None, "history_7d": None}

        history = {}
        try:
            history = await frankfurter_client.get_7day_history(
                base=base, quotes=quotes_list
            )
        except Exception:
            pass

        rates = []
        as_of = None
        for item in data:
            if item["quote"] not in SUPPORTED_CURRENCIES:
                continue
            rates.append(
                ExchangeRateItem(
                    target_currency=item["quote"],
                    rate=float(item["rate"]),
                    date=item["date"],
                    trend_7d=_calc_trend_7d(history, item["quote"], float(item["rate"])),
                )
            )
            if as_of is None or item["date"] > as_of:
                as_of = item["date"]

        history_7d = None
        if history:
            history_7d = {
                currency: [{"date": str(p["date"]), "rate": str(p["rate"])} for p in points]
                for currency, points in history.items()
            }

        return {
            "rates": [r.model_dump() for r in rates],
            "as_of": as_of,
            "history_7d": history_7d,
        }

    result, _ = await cache.get_or_fetch(cache_key, fetch)
    if isinstance(result, dict) and "rates" in result:
        rates = [ExchangeRateItem(**r) for r in result["rates"]]
        return ExchangeRateListResponse(
            base=base,
            as_of=result.get("as_of"),
            rates=rates,
            history_7d=result.get("history_7d"),
        )
    return ExchangeRateListResponse(base=base, rates=[])


@router.get("/historical", response_model=ExchangeRateListResponse)
async def get_historical_rates(
    base: str = Query(default="USD", max_length=3),
    target: str = Query(..., max_length=3),
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
):
    if (to_date - from_date).days > 366:
        raise HTTPException(status_code=400, detail="Date range too wide. Max 1 year.")

    if target not in SUPPORTED_CURRENCIES:
        raise HTTPException(status_code=400, detail=f"Unsupported currency: {target}")

    cache_key = f"exchange_hist:{base}:{target}:{from_date}:{to_date}"

    async def fetch():
        try:
            data = await frankfurter_client.get_historical_rates(
                base=base, quotes=[target], from_date=from_date, to_date=to_date
            )
        except Exception:
            raise HTTPException(status_code=502, detail="External API unavailable")

        rates = [
            ExchangeRateItem(
                target_currency=item["quote"],
                rate=float(item["rate"]),
                date=item["date"],
            )
            for item in data
            if item["quote"] in SUPPORTED_CURRENCIES
        ]

        return {"rates": [r.model_dump() for r in rates]}

    result, _ = await cache.get_or_fetch(cache_key, fetch)
    if isinstance(result, dict) and "rates" in result:
        rates = [ExchangeRateItem(**r) for r in result["rates"]]
        return ExchangeRateListResponse(base=base, rates=rates)
    return ExchangeRateListResponse(base=base, rates=[])


@router.get("/currencies")
async def get_supported_currencies():
    cache_key = "exchange_currencies"

    async def fetch():
        try:
            currencies = await frankfurter_client.get_supported_currencies()
            filtered = {
                c["iso_code"]: c["name"]
                for c in currencies
                if c.get("iso_code") in SUPPORTED_CURRENCIES
            }

            currency_names = {
                code: settings.CURRENCY_NAMES.get(code, name)
                for code, name in filtered.items()
            }
            return currency_names
        except Exception:
            raise HTTPException(status_code=502, detail="External API unavailable")

    result, _ = await cache.get_or_fetch(cache_key, fetch)
    return {"currencies": result}