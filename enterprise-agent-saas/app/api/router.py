from typing import Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.algorithms.code_repair_agent import CodeRepairAgent
from app.core.auth import create_token, get_claims
from app.services.audit_service import AuditService
from app.services.database import get_db
from mvp_api.agents.self_healing import SelfHealingRouter
from mvp_api.algorithms.cognitive_loop import CognitiveLoop
from mvp_api.config import settings
from mvp_api.providers import PROVIDERS, ProviderError

router = APIRouter()
loop = CognitiveLoop(SelfHealingRouter(PROVIDERS))
repair_agent = CodeRepairAgent()


class TokenRequest(BaseModel):
    org_id: str = Field(min_length=1, max_length=100)
    daily_quota: Optional[int] = Field(default=None, ge=1)


class ProcessRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    force_primary_failure: bool = False


@router.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok", "mode": "enterprise"}


@router.post("/v1/auth/token")
def issue_token(req: TokenRequest) -> Dict[str, str]:
    quota = req.daily_quota or settings.default_daily_quota
    return {"access_token": create_token(req.org_id, quota), "token_type": "bearer"}


@router.post("/v1/process")
def process(req: ProcessRequest, claims: Dict = Depends(get_claims), db: Session = Depends(get_db)) -> Dict:
    org_id = claims["org_id"]
    daily_quota = int(claims.get("daily_quota", settings.default_daily_quota))

    payload = req.model_dump()
    payload["text"] = repair_agent.sanitize(payload["text"])
    try:
        result = loop.run(org_id=org_id, payload=payload, daily_quota=daily_quota, scope="enterprise_sync", db=db)
    except ProviderError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    AuditService.write(db, org_id, "/enterprise/v1/process", 200, result)
    return {"org_id": org_id, **result}
