"""Celery app configuration."""

from celery import Celery
from celery.schedules import crontab
from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "job_notification",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["worker.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    # Rate limiting
    task_default_rate_limit="10/m",
    # Beat schedule — periodic tasks
    beat_schedule={
        "scrape-telegram-channels": {
            "task": "worker.tasks.scrape_all_channels",
            "schedule": crontab(hour="*/5", minute=0),  # Every 5 hours
        },
    },
)
