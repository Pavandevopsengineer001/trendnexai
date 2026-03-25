from app.celery_worker import celery_app
from app.main import fetch_and_process

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5})
def fetch_and_process_task(self, limit_per_cat=5):
    return __import__("asyncio").run(fetch_and_process(limit_per_cat))
