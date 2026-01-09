"""Celery Worker Configuration"""
from celery import Celery
from app.core.config import settings


# إنشاء تطبيق Celery
celery_app = Celery(
    "worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# إعدادات Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 دقيقة كحد أقصى للمهمة
    worker_prefetch_multiplier=1,
    worker_concurrency=2,
    task_routes={
        "tasks.generate_video": {"queue": "video"},
        "tasks.generate_image": {"queue": "image"},
        "tasks.generate_voice": {"queue": "voice"},
    }
)


@celery_app.task(bind=True, max_retries=3)
def debug_task(self):
    """مهمة اختبار"""
    print(f"Request: {self.request!r}")
    return True
