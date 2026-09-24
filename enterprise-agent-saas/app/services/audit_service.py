import json
from typing import Dict

from app.models.audit import AuditEvent


class AuditService:
    @staticmethod
    def write(db, org_id: str, endpoint: str, status_code: int, payload: Dict) -> None:
        db.add(
            AuditEvent(
                org_id=org_id,
                endpoint=endpoint,
                status_code=status_code,
                provider_used=payload.get("provider", "unknown"),
                used_fallback=payload.get("used_fallback", False),
                latency_ms=float(payload.get("latency_ms", 0)),
                detail=json.dumps(payload),
            )
        )
        db.commit()
