"""app/auth/dependencies.py — FastAPI dependency for authenticated routes."""
from __future__ import annotations

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.security import decode_token
from app.db.database import get_db
from app.models.user import User
from sqlalchemy.orm import Session

_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    """
    Validates the Bearer access token and returns the authenticated User row.
    Raises 401 on any token issue.
    """
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        user_id = decode_token(credentials.credentials, expected_type="access")
    except (jwt.PyJWTError, ValueError):
        raise exc

    user = db.get(User, user_id)
    if user is None:
        raise exc
    return user
