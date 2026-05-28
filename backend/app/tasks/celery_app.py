from celery import Celery

from app.core.config import settings

celery_app = Celery("safenet", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
celery_app.conf.update(task_serializer="json", result_serializer="json", accept_content=["json"], timezone="UTC")
celery_app.conf.beat_schedule = {
    "missed-checkin-monitor": {
        "task": "safenet.missed_checkin_monitor",
        "schedule": 300.0,
    }
}
