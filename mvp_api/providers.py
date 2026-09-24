import time
from typing import Dict

from mvp_api.config import settings


class ProviderError(Exception):
    """Provider processing failed."""


def _call_primary(payload: Dict) -> Dict:
    if settings.force_primary_failure or payload.get("force_primary_failure"):
        raise TimeoutError("Primary provider timeout")

    latency = settings.primary_latency_ms
    if latency > settings.primary_timeout_ms:
        time.sleep(settings.primary_timeout_ms / 1000)
        raise TimeoutError("Primary provider timeout")

    time.sleep(latency / 1000)
    text = payload.get("text", "")
    return {"output": text.upper(), "latency_ms": latency}


def _call_backup(payload: Dict) -> Dict:
    latency = settings.backup_latency_ms
    time.sleep(latency / 1000)
    text = payload.get("text", "")
    return {"output": text[::-1], "latency_ms": latency}


PROVIDERS = {
    "primary": _call_primary,
    "backup": _call_backup,
}


def execute_with_failover(payload: Dict) -> Dict:
    try:
        result = _call_primary(payload)
        return {**result, "provider": "primary", "used_fallback": False}
    except TimeoutError:
        backup = _call_backup(payload)
        return {**backup, "provider": "backup", "used_fallback": True}
    except Exception as exc:
        raise ProviderError(str(exc)) from exc
