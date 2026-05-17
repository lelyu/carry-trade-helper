from fastapi import APIRouter, Query, HTTPException
from datetime import date

from app.core.cache import cache
from app.core.config import settings
from app.schemas.rates import InterestRateItem, InterestRateListResponse
from app.services.fred_client import fred_client

router = APIRouter(prefix="/api/interest-rates", tags=["interest-rates"])


def _calc_trend_7d(history: dict[str, list[dict]], country: str, current_rate: float) -> float | None:
    points = history.get(country, [])
    if len(points) < 2:
        return None
    old_rate = points[0]["rate"]
    if old_rate == 0:
        return None
    change = current_rate - old_rate
    return round(change, 4)


@router.get("/latest", response_model=InterestRateListResponse)
async def get_latest_rates():
    cache_key = "interest_latest"

    async def fetch():
        countries = fred_client.ALL_COUNTRIES

        try:
            data = await fred_client.get_interest_rates(country_codes=countries)
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"External API unavailable: {str(e)}")

        if not data:
            return {"rates": [], "as_of": None, "history_7d": None}

        history = {}
        try:
            history = await fred_client.get_7day_history(country_codes=countries)
        except Exception:
            pass

        rates = []
        as_of = None
        for item in data:
            country = item["country_code"]
            rate_val = float(item["rate"])
            rate_date = item.get("date")
            if rate_date:
                try:
                    rate_date = date.fromisoformat(str(rate_date))
                except (ValueError, TypeError):
                    rate_date = None

            if as_of is None or (rate_date and rate_date > as_of):
                as_of = rate_date

            rates.append(
                InterestRateItem(
                    country_code=country,
                    currency_code=item["currency_code"],
                    country_name=settings.COUNTRY_NAMES.get(country, country),
                    rate=float(item["rate"]),
                    date=rate_date,
                    trend_7d=_calc_trend_7d(history, country, rate_val),
                ).model_dump()
            )

        history_7d = None
        if history:
            history_7d = {
                country: [
                    {"date": str(p["date"]), "rate": str(p["rate"])} for p in points
                ]
                for country, points in history.items()
            }

        return {"rates": rates, "as_of": str(as_of) if as_of else None, "history_7d": history_7d}

    result, _ = await cache.get_or_fetch(cache_key, fetch)
    if isinstance(result, dict) and "rates" in result:
        rates = [InterestRateItem(**r) for r in result["rates"]]
        as_of = None
        if result.get("as_of"):
            try:
                as_of = date.fromisoformat(result["as_of"])
            except (ValueError, TypeError):
                pass
        return InterestRateListResponse(
            as_of=as_of,
            rates=rates,
            history_7d=result.get("history_7d"),
        )
    return InterestRateListResponse(rates=[])


@router.get("/historical", response_model=InterestRateListResponse)
async def get_historical_rates(
    country: str = Query(..., max_length=3),
    from_date: date = Query(..., alias="from"),
    to_date: date = Query(..., alias="to"),
):
    if (to_date - from_date).days > 3650:
        raise HTTPException(status_code=400, detail="Date range too wide. Max 10 years.")

    cache_key = f"interest_hist:{country}:{from_date}:{to_date}"

    async def fetch():
        try:
            history = await fred_client.get_historical_rates(
                country_codes=[country], from_date=from_date, to_date=to_date
            )
        except Exception:
            raise HTTPException(status_code=502, detail="External API unavailable")

        rates = []
        for country_code, points in history.items():
            for p in points:
                rates.append(
                    InterestRateItem(
                        country_code=country_code,
                        currency_code=fred_client.COUNTRY_CURRENCY_MAP.get(
                            country_code, country_code[:3]
                        ),
                        country_name=settings.COUNTRY_NAMES.get(
                            country_code, country_code
                        ),
                        rate=float(p["rate"]),
                        date=date.fromisoformat(str(p["date"])),
                    ).model_dump()
                )

        return {"rates": rates}

    result, _ = await cache.get_or_fetch(cache_key, fetch)
    if isinstance(result, dict) and "rates" in result:
        rates = [InterestRateItem(**r) for r in result["rates"]]
        return InterestRateListResponse(rates=rates)
    return InterestRateListResponse(rates=[])