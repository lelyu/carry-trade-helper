from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "carry_trade",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.fetch_rates", "app.tasks.send_reports"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_connection_retry_on_startup=True,
)

celery_app.conf.beat_schedule = {
    "fetch-rates-every-6-hours": {
        "task": "app.tasks.fetch_rates.fetch_and_cache_rates",
        "schedule": crontab(hour="*/6"),
    },
    "send-daily-reports": {
        "task": "app.tasks.send_reports.send_daily_reports",
        "schedule": crontab(hour=8, minute=0),
    },
}
