import asyncio
from datetime import date
from enum import Enum
from sqlalchemy import select

from app.tasks.celery_app import celery_app
from app.core.database import async_session_maker
from app.models.user import User
from app.models.subscription import UserPreferences
from app.models.rates import ExchangeRate, InterestRate
from app.services.resend_client import send_daily_report


class EmailFrequency(str, Enum):
    DAILY = "daily"
    HOURLY = "hourly"
    WEEKLY = "weekly"


@celery_app.task
def send_daily_reports():
    """Send daily reports to all active subscribers"""
    return asyncio.run(_send_reports_by_frequency(EmailFrequency.DAILY))


@celery_app.task
def send_hourly_reports():
    """Send hourly reports to subscribers with hourly frequency"""
    return asyncio.run(_send_reports_by_frequency(EmailFrequency.HOURLY))


async def _send_reports_by_frequency(frequency: EmailFrequency):
    match frequency:
        case EmailFrequency.DAILY:
            return await _send_daily_reports()
        case EmailFrequency.HOURLY:
            return await _send_hourly_reports()
        case _:
            return {"status": "error", "message": f"Unknown frequency: {frequency}"}


async def _send_daily_reports():
    async with async_session_maker() as db:
        try:
            result = await db.execute(
                select(UserPreferences)
                .where(UserPreferences.is_active == True)
                .where(UserPreferences.email_frequency == EmailFrequency.DAILY.value)
            )
            preferences = result.scalars().all()

            exchange_rates = await _get_latest_exchange_rates(db)
            interest_rates = await _get_latest_interest_rates(db)

            for pref in preferences:
                user_result = await db.execute(
                    select(User).where(User.id == pref.user_id)
                )
                user = user_result.scalar_one_or_none()

                if user and user.is_verified:
                    relevant_rates = {
                        pair: exchange_rates.get(pair)
                        for pair in pref.currency_pairs
                        if pair in exchange_rates
                    }

                    report_data = {
                        "date": date.today().isoformat(),
                        "exchange_rates": relevant_rates,
                        "interest_rates": interest_rates,
                    }

                    await send_daily_report(user.email, report_data)

            return {
                "status": "success",
                "message": f"Sent {len(preferences)} daily reports",
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}


async def _send_hourly_reports():
    async with async_session_maker() as db:
        try:
            result = await db.execute(
                select(UserPreferences)
                .where(UserPreferences.is_active == True)
                .where(UserPreferences.email_frequency == EmailFrequency.HOURLY.value)
            )
            preferences = result.scalars().all()

            for pref in preferences:
                pass

            return {
                "status": "success",
                "message": f"Sent {len(preferences)} hourly reports",
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}


async def _get_latest_exchange_rates(db):
    """Get latest exchange rates"""
    result = await db.execute(
        select(ExchangeRate).where(ExchangeRate.date == date.today())
    )
    rates = result.scalars().all()

    return {
        f"{rate.base_currency}/{rate.target_currency}": float(rate.rate)
        for rate in rates
    }


async def _get_latest_interest_rates(db):
    """Get latest interest rates"""
    result = await db.execute(
        select(InterestRate).where(InterestRate.date == date.today())
    )
    rates = result.scalars().all()

    return {rate.country_code: float(rate.rate) for rate in rates}
