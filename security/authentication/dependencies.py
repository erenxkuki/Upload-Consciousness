"""Authentication dependency for FastAPI."""
from __future__ import annotations

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from security.authentication.auth import decode_access_token

bearer = HTTPBearer(auto_error=False)


async def get_current_principal(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)):
    if credentials is None:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
    except ValueError:
        raise HTTPException(status_code=401, detail="invalid token")
    return {"user_id": payload.get("sub"), "role": payload.get("role", "guest")}


def require_role(minimum: str):
    from security.authorization.policy import has_role

    async def dep(principal=Depends(get_current_principal)):
        if principal is None:
            raise HTTPException(status_code=401, detail="authentication required")
        if not has_role(principal["role"], minimum):
            raise HTTPException(status_code=403, detail="insufficient role")
        return principal

    return dep
