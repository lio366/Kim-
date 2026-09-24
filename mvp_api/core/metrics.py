import logging

from prometheus_client import Counter

logger = logging.getLogger("kimi.autonomy")

AUTONOMOUS_DECISIONS = Counter(
    "kimi_autonomous_decisions_total",
    "Autonomous decisions taken by the cognitive loop",
    ["tenant", "route"],
)
HUMAN_INTERVENTIONS = Counter(
    "kimi_human_interventions_total",
    "Manual interventions requested",
    ["tenant", "reason"],
)
ROLLBACKS = Counter(
    "kimi_rollbacks_total",
    "Execution rollbacks triggered",
    ["tenant", "reason"],
)
FAILOVER_EVENTS = Counter(
    "kimi_failover_events_total",
    "Failovers from preferred provider to backup",
    ["tenant", "from_provider", "to_provider"],
)
WORKFLOW_STAGE_EVENTS = Counter(
    "kimi_workflow_stage_events_total",
    "Workflow stage events",
    ["tenant", "stage", "status"],
)


def trace_workflow(tenant: str, workflow_id: str, stage: str, status: str, detail: str = "") -> None:
    WORKFLOW_STAGE_EVENTS.labels(tenant=tenant, stage=stage, status=status).inc()
    logger.info(
        "workflow_trace",
        extra={
            "tenant": tenant,
            "workflow_id": workflow_id,
            "stage": stage,
            "status": status,
            "detail": detail,
        },
    )
