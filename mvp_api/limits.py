from datetime import datetime, timezone

import redis
from fastapi import HTTPException

from mvp_api.config import settings


redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)


def _current_day_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def enforce_limits(org_id: str, daily_quota: int, scope: str = "api") -> None:
    minute_key = f"rl:{scope}:{org_id}:{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}"
    daily_key = f"quota:{scope}:{org_id}:{_current_day_key()}"

    minute_value = redis_client.incr(minute_key)
    if minute_value == 1:
        redis_client.expire(minute_key, 65)

    if minute_value > settings.rate_limit_per_minute:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    day_value = redis_client.incr(daily_key)
    if day_value == 1:
        redis_client.expire(daily_key, 60 * 60 * 24 + 60)

    if day_value > daily_quota:
        raise HTTPException(status_code=402, detail="Quota exceeded")
