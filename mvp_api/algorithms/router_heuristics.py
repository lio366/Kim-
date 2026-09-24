from dataclasses import dataclass
from typing import Dict


@dataclass
class RouteStats:
    successes: int = 0
    failures: int = 0
    avg_latency_ms: float = 0.0


class RouterHeuristics:
    """Learns from operational outcomes to choose a provider route."""

    def __init__(self) -> None:
        self._stats: Dict[str, RouteStats] = {
            "primary": RouteStats(),
            "backup": RouteStats(),
        }

    def choose_route(self, health: Dict[str, Dict[str, float]]) -> str:
        primary_health = health.get("primary", {}).get("health_score", 100)
        backup_health = health.get("backup", {}).get("health_score", 100)
        primary_latency = self._stats["primary"].avg_latency_ms or 120
        backup_latency = self._stats["backup"].avg_latency_ms or 220

        if primary_health < 45 and backup_health >= primary_health:
            return "backup"
        if backup_latency + 40 < primary_latency and backup_health > 70:
            return "backup"
        return "primary"

    def record(self, provider: str, success: bool, latency_ms: float) -> None:
        stat = self._stats[provider]
        if success:
            stat.successes += 1
        else:
            stat.failures += 1

        if latency_ms > 0:
            total_calls = max(stat.successes + stat.failures, 1)
            stat.avg_latency_ms = ((stat.avg_latency_ms * (total_calls - 1)) + latency_ms) / total_calls

    def snapshot(self) -> Dict[str, Dict[str, float]]:
        return {
            provider: {
                "successes": stats.successes,
                "failures": stats.failures,
                "avg_latency_ms": round(stats.avg_latency_ms, 2),
            }
            for provider, stats in self._stats.items()
        }


router_heuristics = RouterHeuristics()
