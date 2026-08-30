"""
JWT token creation and verification.
Used by the admin login endpoint and the verify_jwt FastAPI dependency.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from fastapi import HTTPException, status

from app.config import settings

_ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a signed JWT access token.

    Args:
        data:          Payload dict — typically {"sub": username}.
        expires_delta: Override for token lifetime; defaults to JWT_EXPIRY_HOURS.

    Returns:
        Signed JWT string.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta else timedelta(hours=settings.JWT_EXPIRY_HOURS)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=_ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate a JWT token.

    Raises:
        HTTPException 401 if the token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
