from celery import Celery
from typing import Optional

from mvp_api.agents.self_healing import SelfHealingRouter
from mvp_api.algorithms.cognitive_loop import CognitiveLoop
from mvp_api.config import settings
from mvp_api.db import SessionLocal
from mvp_api.providers import PROVIDERS


celery_app = Celery(
    "kimi_mvp",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)


cognitive_loop: Optional[CognitiveLoop] = CognitiveLoop(SelfHealingRouter(PROVIDERS))


def set_cognitive_loop(loop: CognitiveLoop) -> None:
    global cognitive_loop
    cognitive_loop = loop


@celery_app.task(name="mvp_api.process_payload")
def process_payload(org_id: str, daily_quota: int, payload: dict) -> dict:
    if cognitive_loop is None:
        raise RuntimeError("Cognitive loop is not initialized")

    db = SessionLocal()
    try:
        result = cognitive_loop.run(
            org_id=org_id,
            payload=payload,
            daily_quota=daily_quota,
            scope="worker",
            db=db,
        )
    finally:
        db.close()

    return {"org_id": org_id, **result}
