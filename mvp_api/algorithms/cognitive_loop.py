import json
import uuid
from typing import Dict

from mvp_api.agents.self_healing import SelfHealingRouter
from mvp_api.algorithms.router_heuristics import router_heuristics
from mvp_api.core.guardrails import policy
from mvp_api.core.metrics import (
    AUTONOMOUS_DECISIONS,
    FAILOVER_EVENTS,
    ROLLBACKS,
    trace_workflow,
)
from mvp_api.models import AuditEvent


class CognitiveLoop:
    """Formal autonomous loop: detect -> prioritize -> execute -> audit -> learn."""

    def __init__(self, executor: SelfHealingRouter) -> None:
        self.executor = executor

    def run(self, org_id: str, payload: Dict, daily_quota: int, scope: str, db=None) -> Dict:
        workflow_id = str(uuid.uuid4())

        trace_workflow(org_id, workflow_id, "detect", "ok", "input received")
        context = {
            "text_size": len(payload.get("text", "")),
            "force_primary_failure": payload.get("force_primary_failure", False),
        }

        trace_workflow(org_id, workflow_id, "prioritize", "ok", "guardrails")
        policy.evaluate(org_id=org_id, text=payload.get("text", ""), daily_quota=daily_quota, scope=scope)

        preferred_route = router_heuristics.choose_route(self.executor.snapshot())
        AUTONOMOUS_DECISIONS.labels(tenant=org_id, route=preferred_route).inc()

        trace_workflow(org_id, workflow_id, "execute", "start", f"preferred={preferred_route}")
        try:
            execution = self.executor.execute(payload, preferred=preferred_route)
        except Exception as exc:  # noqa: BLE001
            policy.record_failure()
            router_heuristics.record(provider=preferred_route, success=False, latency_ms=0)
            ROLLBACKS.labels(tenant=org_id, reason="provider_failure").inc()
            trace_workflow(org_id, workflow_id, "execute", "error", str(exc))
            raise

        policy.record_success()
        used_fallback = execution.get("provider") != preferred_route
        if used_fallback:
            FAILOVER_EVENTS.labels(
                tenant=org_id,
                from_provider=preferred_route,
                to_provider=execution.get("provider", "unknown"),
            ).inc()

        trace_workflow(org_id, workflow_id, "audit", "ok", "event recorded")
        audit_detail = {
            "workflow_id": workflow_id,
            "strategy": preferred_route,
            "used_fallback": used_fallback,
            "health_snapshot": self.executor.snapshot(),
            "route_learning": router_heuristics.snapshot(),
            "context": context,
        }

        if db is not None:
            db.add(
                AuditEvent(
                    org_id=org_id,
                    endpoint=f"/{scope}",
                    status_code=200,
                    provider_used=execution.get("provider", "unknown"),
                    used_fallback=used_fallback,
                    latency_ms=float(execution.get("latency_ms", 0)),
                    detail=json.dumps(audit_detail),
                )
            )
            db.commit()

        trace_workflow(org_id, workflow_id, "learn", "ok", "heuristics updated")
        router_heuristics.record(
            provider=execution.get("provider", "primary"),
            success=True,
            latency_ms=float(execution.get("latency_ms", 0)),
        )

        return {
            "workflow_id": workflow_id,
            "strategy": preferred_route,
            "used_fallback": used_fallback,
            **execution,
        }
