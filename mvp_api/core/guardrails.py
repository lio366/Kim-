from datetime import datetime, timezone

import redis
from fastapi import HTTPException

from mvp_api.config import settings
from mvp_api.limits import enforce_limits

redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _current_day() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


class GuardrailPolicy:
    """Central policy for risk, cost, quotas and global circuit breaker."""

    def __init__(self) -> None:
        self.error_key = "guardrails:global_errors"
        self.open_until_key = "guardrails:global_circuit_open_until"

    def _ensure_not_killed(self) -> None:
        if settings.kill_switch_enabled:
            raise HTTPException(status_code=503, detail="System kill switch enabled")

    def _ensure_circuit_closed(self) -> None:
        open_until = redis_client.get(self.open_until_key)
        if open_until and float(open_until) > datetime.now(timezone.utc).timestamp():
            raise HTTPException(status_code=503, detail="Global circuit breaker open")

    def _enforce_budget(self, org_id: str, text: str) -> None:
        estimated_cost = (max(len(text), 1) / 1000.0) * settings.cost_per_1k_chars
        key = f"budget:{org_id}:{_current_day()}"
        total = redis_client.incrbyfloat(key, estimated_cost)
        if total == estimated_cost:
            redis_client.expire(key, 60 * 60 * 24 + 60)
        if total > settings.max_budget_per_day:
            raise HTTPException(status_code=402, detail="Daily budget exceeded")

    def evaluate(self, org_id: str, text: str, daily_quota: int, scope: str) -> None:
        self._ensure_not_killed()
        self._ensure_circuit_closed()
        self._enforce_budget(org_id, text)
        enforce_limits(org_id, daily_quota, scope=scope)

    def record_failure(self) -> None:
        errors = redis_client.incr(self.error_key)
        redis_client.expire(self.error_key, settings.global_circuit_window_seconds)
        if errors >= settings.global_circuit_error_threshold:
            open_until = datetime.now(timezone.utc).timestamp() + settings.global_circuit_cooldown_seconds
            redis_client.set(self.open_until_key, str(open_until), ex=settings.global_circuit_cooldown_seconds)

    def record_success(self) -> None:
        redis_client.delete(self.error_key)


policy = GuardrailPolicy()
