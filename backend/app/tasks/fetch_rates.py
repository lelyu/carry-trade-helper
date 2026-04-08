from datetime import date
from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.core.database import async_session_maker
from app.models.rates import ExchangeRate, InterestRate
from app.models.subscription import UserPreferences
from app.services.frankfurter_client import frankfurter_client
from app.services.fred_client import fred_client
from app.core.config import settings
import asyncio


@celery_app.task
def fetch_and_cache_rates():
    """Fetch latest exchange and interest rates from APIs"""
    return asyncio.run(_fetch_and_cache_rates())


async def _fetch_and_cache_rates():
    async with async_session_maker() as db:
        try:
            exchange_data = await frankfurter_client.get_latest_rates(
                base="USD", quotes=settings.SUPPORTED_CURRENCIES
            )

            if exchange_data and "rates" in exchange_data:
                for target, rate_value in exchange_data["rates"].items():
                    existing = await db.execute(
                        select(ExchangeRate)
                        .where(ExchangeRate.base_currency == "USD")
                        .where(ExchangeRate.target_currency == target)
                        .where(ExchangeRate.date == date.today())
                    )
                    existing = existing.scalar_one_or_none()

                    if not existing:
                        rate = ExchangeRate(
                            base_currency="USD",
                            target_currency=target,
                            rate=rate_value,
                            date=date.today(),
                        )
                        db.add(rate)

            interest_data = await fred_client.get_interest_rates(
                country_codes=[
                    "USA",
                    "EUR",
                    "GBR",
                    "JPN",
                    "CHF",
                    "AUD",
                    "CAD",
                    "NZD",
                    "CHN",
                    "HKG",
                ]
            )

            for rate_data in interest_data:
                existing = await db.execute(
                    select(InterestRate)
                    .where(InterestRate.country_code == rate_data["country_code"])
                    .where(InterestRate.date == date.today())
                )
                existing = existing.scalar_one_or_none()

                if not existing:
                    rate = InterestRate(
                        country_code=rate_data["country_code"],
                        currency_code=rate_data["currency_code"],
                        rate=rate_data["rate"],
                        rate_type=rate_data.get("rate_type", "policy_rate"),
                        date=date.today(),
                    )
                    db.add(rate)

            await db.commit()
            return {
                "status": "success",
                "message": "Rates fetched and cached successfully",
            }

        except Exception as e:
            await db.rollback()
            return {"status": "error", "message": str(e)}


@celery_app.task
def check_threshold_alerts():
    """Check user-defined alert thresholds and send notifications"""
    return asyncio.run(_check_threshold_alerts())


async def _check_threshold_alerts():
    async with async_session_maker() as db:
        try:
            result = await db.execute(
                select(UserPreferences).where(UserPreferences.is_active == True)
            )
            preferences = result.scalars().all()

            for pref in preferences:
                if pref.alert_thresholds:
                    await _check_user_thresholds(db, pref)

            return {"status": "success", "message": "Threshold alerts checked"}

        except Exception as e:
            return {"status": "error", "message": str(e)}


async def _check_user_thresholds(db, preferences):
    """Check thresholds for a specific user"""
    pass
