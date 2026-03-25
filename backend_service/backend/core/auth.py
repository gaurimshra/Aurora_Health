import os

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.services.auth_service import get_user_by_token, upsert_external_user

try:
    import jwt
except Exception:  # pragma: no cover
    jwt = None


bearer_scheme = HTTPBearer(auto_error=False)
CLERK_JWT_VERIFICATION_KEY = os.getenv("CLERK_JWT_VERIFICATION_KEY")


def _get_clerk_user(token: str) -> dict | None:
    if not CLERK_JWT_VERIFICATION_KEY or jwt is None:
        return None
    try:
        claims = jwt.decode(
            token,
            CLERK_JWT_VERIFICATION_KEY,
            algorithms=["RS256", "HS256"],
            options={"verify_aud": False},
        )
    except Exception:
        return None

    external_user = {
        "user_id": claims.get("sub") or claims.get("user_id"),
        "email": claims.get("email") or claims.get("primary_email_address", "clerk-user@example.com"),
        "name": claims.get("name") or claims.get("username") or "Clerk User",
        "username": claims.get("username") or claims.get("preferred_username"),
        "auth_provider": "clerk",
    }
    if not external_user["user_id"]:
        return None
    return upsert_external_user(external_user)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    try:
        return get_user_by_token(credentials.credentials)
    except HTTPException:
        clerk_user = _get_clerk_user(credentials.credentials)
        if clerk_user is not None:
            return clerk_user
        raise
