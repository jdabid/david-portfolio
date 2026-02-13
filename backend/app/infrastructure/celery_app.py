"""
Celery application configuration.
Uses RabbitMQ as broker and Redis as result backend.
"""

from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "portfolio_worker",
    broker=settings.rabbitmq_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Retry policy
    task_acks_late=True,
    worker_prefetch_multiplier=1,

    # Dead Letter Queue
    task_reject_on_worker_lost=True,

    # Task routing
    task_routes={
        "contact.send_email": {"queue": "email.send"},
        "analytics.aggregate_daily": {"queue": "analytics.aggregate"},
    },

    # Auto-discover tasks in feature slices
    include=[
        "app.features.contact.tasks.send_email",
        "app.features.analytics.tasks.aggregate_metrics",
    ],

    # Celery Beat schedule — periodic tasks
    beat_schedule={
        "aggregate-daily-metrics": {
            "task": "analytics.aggregate_daily",
            "schedule": crontab(minute=0),  # Every hour at :00
        },
    },
)
