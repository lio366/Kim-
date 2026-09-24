import json
import time
from typing import Dict

from celery.result import AsyncResult
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from sqlalchemy.orm import Session
from starlette.responses import Response

from mvp_api.auth import create_token, get_claims
from mvp_api.config import settings
from mvp_api.db import Base, engine, get_db
from mvp_api.limits import enforce_limits
from mvp_api.models import AuditEvent
from mvp_api.providers import ProviderError, execute_with_failover
from mvp_api.tasks import celery_app, process_payload

app = FastAPI(title="KIMI MVP API", version="0.1.0")

REQUEST_COUNT = Counter("kimi_requests_total", "Total HTTP requests", ["endpoint", "org_id", "status"])
REQUEST_LATENCY = Histogram("kimi_request_latency_seconds", "HTTP latency", ["endpoint"])
FALLBACK_COUNT = Counter("kimi_failover_total", "Failovers to backup provider", ["endpoint", "org_id"])


class TokenRequest(BaseModel):
    org_id: str = Field(min_length=1, max_length=100)
    daily_quota: int | None = Field(default=None, ge=1)


class ProcessRequest(BaseModel):
    text: str = Field(min_length=1, max_length=2000)
    force_primary_failure: bool = False


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/auth/token")
def issue_token(req: TokenRequest) -> Dict[str, str]:
    quota = req.daily_quota or settings.default_daily_quota
    return {"access_token": create_token(req.org_id, quota), "token_type": "bearer"}


@app.post("/v1/process")
def process_sync(
    req: ProcessRequest,
    claims: Dict = Depends(get_claims),
    db: Session = Depends(get_db),
) -> Dict:
    org_id = claims["org_id"]
    daily_quota = int(claims.get("daily_quota", settings.default_daily_quota))
    enforce_limits(org_id, daily_quota)

    start = time.perf_counter()
    try:
        result = execute_with_failover(req.model_dump())
        status_code = 200
    except ProviderError as exc:
        status_code = 500
        REQUEST_COUNT.labels("/v1/process", org_id, str(status_code)).inc()
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        elapsed = time.perf_counter() - start
        REQUEST_LATENCY.labels("/v1/process").observe(elapsed)

    if result["used_fallback"]:
        FALLBACK_COUNT.labels("/v1/process", org_id).inc()

    db.add(
        AuditEvent(
            org_id=org_id,
            endpoint="/v1/process",
            status_code=status_code,
            provider_used=result["provider"],
            used_fallback=result["used_fallback"],
            latency_ms=result["latency_ms"],
            detail=json.dumps({"text_size": len(req.text)}),
        )
    )
    db.commit()

    REQUEST_COUNT.labels("/v1/process", org_id, str(status_code)).inc()
    return {"org_id": org_id, **result}


@app.post("/v1/process/async")
def process_async(req: ProcessRequest, claims: Dict = Depends(get_claims)) -> Dict[str, str]:
    org_id = claims["org_id"]
    daily_quota = int(claims.get("daily_quota", settings.default_daily_quota))
    enforce_limits(org_id, daily_quota)

    task = process_payload.delay(org_id, req.model_dump())
    REQUEST_COUNT.labels("/v1/process/async", org_id, "202").inc()
    return {"task_id": task.id, "status": "queued"}


@app.get("/v1/tasks/{task_id}")
def task_status(task_id: str, claims: Dict = Depends(get_claims)) -> Dict:
    org_id = claims["org_id"]
    result = AsyncResult(task_id, app=celery_app)
    payload = result.result if result.successful() else None

    if isinstance(payload, dict) and payload.get("org_id") != org_id:
        raise HTTPException(status_code=403, detail="Task does not belong to this org")

    return {
        "task_id": task_id,
        "status": result.status,
        "result": payload,
    }
