from celery import Celery

from mvp_api.config import settings
from mvp_api.providers import execute_with_failover


celery_app = Celery(
    "kimi_mvp",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


@celery_app.task(name="mvp_api.process_payload")
def process_payload(org_id: str, payload: dict) -> dict:
    result = execute_with_failover(payload)
    return {"org_id": org_id, **result}
