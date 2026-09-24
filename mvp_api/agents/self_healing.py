import time
from dataclasses import dataclass
from threading import Lock
from typing import Callable, Dict, List, Optional


@dataclass
class ProviderState:
    health_score: float = 100.0
    consecutive_failures: int = 0
    backoff_seconds: int = 0
    circuit_open_until: float = 0.0


class SelfHealingRouter:
    """Provider manager with backoff, health-score and controlled reintegration."""

    def __init__(self, providers: Dict[str, Callable[[Dict], Dict]]) -> None:
        self.providers = providers
        self._lock = Lock()
        self.state = {name: ProviderState() for name in providers.keys()}

    def _is_available(self, provider: str) -> bool:
        return self.state[provider].circuit_open_until <= time.time()

    def _record_success(self, provider: str) -> None:
        with self._lock:
            st = self.state[provider]
            st.consecutive_failures = 0
            st.backoff_seconds = 0
            st.circuit_open_until = 0.0
            st.health_score = min(100.0, st.health_score + 8.0)

    def _record_failure(self, provider: str) -> None:
        with self._lock:
            st = self.state[provider]
            st.consecutive_failures += 1
            st.backoff_seconds = max(1, min(60, 2 ** st.consecutive_failures))
            st.circuit_open_until = time.time() + st.backoff_seconds
            st.health_score = max(0.0, st.health_score - (12.0 + st.consecutive_failures))

    def snapshot(self) -> Dict[str, Dict[str, float]]:
        now = time.time()
        return {
            provider: {
                "health_score": round(st.health_score, 2),
                "consecutive_failures": st.consecutive_failures,
                "available": st.circuit_open_until <= now,
            }
            for provider, st in self.state.items()
        }

    def execute(self, payload: Dict, preferred: str = "primary") -> Dict:
        ordered: List[str] = [preferred] + [name for name in self.providers if name != preferred]

        last_error: Optional[Exception] = None
        for provider in ordered:
            if not self._is_available(provider):
                continue
            try:
                response = self.providers[provider](payload)
                self._record_success(provider)
                response["provider"] = provider
                return response
            except Exception as exc:  # noqa: BLE001
                self._record_failure(provider)
                last_error = exc

        # If all circuits are open, give primary a controlled reintegration attempt.
        try:
            response = self.providers["primary"](payload)
            self._record_success("primary")
            response["provider"] = "primary"
            return response
        except Exception as exc:  # noqa: BLE001
            self._record_failure("primary")
            last_error = exc

        if last_error is None:
            raise RuntimeError("No provider available")
        raise last_error
