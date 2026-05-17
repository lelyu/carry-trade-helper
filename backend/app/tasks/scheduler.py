import asyncio
import logging
from datetime import date

from app.core.cache import cache
from app.core.config import settings
from app.schemas.rates import ExchangeRateItem, InterestRateItem
from app.services.frankfurter_client import frankfurter_client
from app.services.fred_client import fred_client

logger = logging.getLogger(__name__)

SUPPORTED_CURRENCIES = {
    "USD", "EUR", "GBP", "JPY", "CHF", "AUD", "CAD", "NZD", "CNY", "HKD",
}


def _calc_trend_7d_exchange(
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


def _calc_trend_7d_interest(
    history: dict[str, list[dict]], country: str, current_rate: float
) -> float | None:
    points = history.get(country, [])
    if len(points) < 2:
        return None
    old_rate = points[0]["rate"]
    if old_rate == 0:
        return None
    change = current_rate - old_rate
    return round(change, 4)


async def prefetch_exchange_rates() -> None:
    for base in ["USD", "EUR"]:
        cache_key = f"exchange_latest:{base}"
        quotes_list = list(SUPPORTED_CURRENCIES - {base})

        try:
            data = await frankfurter_client.get_latest_rates(
                base=base, quotes=quotes_list
            )
        except Exception as e:
            logger.warning("Prefetch exchange rates (%s) failed: %s", base, e)
            continue

        if not data:
            continue

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
                    trend_7d=_calc_trend_7d_exchange(
                        history, item["quote"], float(item["rate"])
                    ),
                )
            )
            if as_of is None or item["date"] > as_of:
                as_of = item["date"]

        history_7d = None
        if history:
            history_7d = {
                currency: [
                    {"date": str(p["date"]), "rate": str(p["rate"])}
                    for p in points
                ]
                for currency, points in history.items()
            }

        cache.set(
            cache_key,
            {
                "rates": [r.model_dump() for r in rates],
                "as_of": as_of,
                "history_7d": history_7d,
            },
        )
        logger.info("Prefetched exchange rates (base=%s)", base)

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
        cache.set("exchange_currencies", currency_names)
        logger.info("Prefetched exchange currencies")
    except Exception as e:
        logger.warning("Prefetch currencies failed: %s", e)


async def prefetch_interest_rates() -> None:
    countries = fred_client.ALL_COUNTRIES
    cache_key = "interest_latest"

    try:
        data = await fred_client.get_interest_rates(country_codes=countries)
    except Exception as e:
        logger.warning("Prefetch interest rates failed: %s", e)
        return

    if not data:
        return

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
                trend_7d=_calc_trend_7d_interest(history, country, rate_val),
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

    cache.set(
        cache_key,
        {
            "rates": rates,
            "as_of": str(as_of) if as_of else None,
            "history_7d": history_7d,
        },
    )
    logger.info("Prefetched interest rates")


async def prefetch_all() -> None:
    logger.info("Starting prefetch: exchange rates + interest rates")
    await asyncio.gather(
        prefetch_exchange_rates(),
        prefetch_interest_rates(),
        return_exceptions=True,
    )
    logger.info("Prefetch complete")


async def scheduler_loop(interval: int) -> None:
    while True:
        await asyncio.sleep(interval)
        try:
            await prefetch_all()
        except Exception as e:
            logger.error("Scheduler prefetch error: %s", e)