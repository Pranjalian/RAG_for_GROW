"""
Shared FastAPI dependencies — reusable Depends() targets.
"""

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt_handler import decode_token
from app.db.session import AsyncSession, get_db  # re-export for convenience

_bearer_scheme = HTTPBearer(auto_error=False)


async def verify_jwt(
    credentials: HTTPAuthorizationCredentials = Security(_bearer_scheme),
) -> dict:
    """
    FastAPI dependency that validates the Bearer JWT token.

    Usage:
        @router.get("/protected")
        async def endpoint(token_data: dict = Depends(verify_jwt)):
            ...

    Raises:
        HTTPException 401 if the token is missing or invalid.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return decode_token(credentials.credentials)


# Re-export get_db so route files only need to import from deps
__all__ = ["get_db", "verify_jwt", "AsyncSession"]
