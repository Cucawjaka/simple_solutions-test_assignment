from celery import Celery
from celery.schedules import crontab

from config import RedisConfig

redis_config = RedisConfig()

celery_app = Celery(
    "price_service",
    broker=redis_config.broker_url,
    include=["infrastructure.polling.celery_worker"],
)

celery_app.conf.update(
    beat_schedule={
        "collect-prices-every-minute": {
            "task": "collect_prices",
            "schedule": crontab(minute="*"),
        },
    },
    timezone="UTC",
    enable_utc=True,
    task_ignore_result=True,
)
