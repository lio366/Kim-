from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from mvp_api.config import settings

security = HTTPBearer()


def create_token(org_id: str, daily_quota: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": org_id,
        "org_id": org_id,
        "daily_quota": daily_quota,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_exp_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_claims(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict:
    token = credentials.credentials
    try:
        claims = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        if not claims.get("org_id"):
            raise ValueError("missing org_id")
        return claims
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc
