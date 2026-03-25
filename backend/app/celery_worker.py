from celery import Celery
import os

BROKER_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")
BACKEND_URL = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

celery_app = Celery(
    "trendnexai",
    broker=BROKER_URL,
    backend=BACKEND_URL,
)

celery_app.conf.task_routes = {
    "app.tasks.fetch_and_process_task": {"queue": "news"}
}

celery_app.conf.task_annotations = {
    "app.tasks.fetch_and_process_task": {"rate_limit": "10/m"}
}
