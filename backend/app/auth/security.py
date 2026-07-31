"""
app/auth/security.py — Password hashing and JWT creation/decoding.

Design notes:
- Two token types (access / refresh) are embedded in each JWT as a `type` claim.
  decode_token() rejects a token used as the wrong type — an access token cannot
  be presented as a refresh token and vice versa.
- /auth/refresh performs full rotation: issues a brand-new pair, not just a new
  access token, limiting the re-use window of a stolen refresh token.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from app.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
_BCRYPT_MAX_PASSWORD_BYTES = 72


def _normalize_password_for_bcrypt(plain: str) -> str:
    """bcrypt only accepts passwords up to 72 bytes; truncate safely before hashing."""
    encoded = plain.encode("utf-8")
    if len(encoded) <= _BCRYPT_MAX_PASSWORD_BYTES:
        return plain
    return encoded[:_BCRYPT_MAX_PASSWORD_BYTES].decode("utf-8", errors="ignore")


# ── Password hashing ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return _pwd_context.hash(_normalize_password_for_bcrypt(plain))


def verify_password(plain: str, hashed: str) -> bool:
    return _pwd_context.verify(_normalize_password_for_bcrypt(plain), hashed)


# ── JWT ───────────────────────────────────────────────────────────────────────

def _create_token(sub: str, token_type: str, expire_delta: timedelta) -> str:
    now = datetime.now(tz=timezone.utc)
    payload = {
        "sub": sub,
        "type": token_type,
        "iat": now,
        "exp": now + expire_delta,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(user_id: str) -> str:
    return _create_token(
        user_id, "access", timedelta(minutes=settings.access_token_expire_minutes)
    )


def create_refresh_token(user_id: str) -> str:
    return _create_token(
        user_id, "refresh", timedelta(days=settings.refresh_token_expire_days)
    )


def create_token_pair(user_id: str) -> dict:
    return {
        "access_token": create_access_token(user_id),
        "refresh_token": create_refresh_token(user_id),
        "token_type": "bearer",
    }


def decode_token(token: str, expected_type: str) -> str:
    """
    Decode a JWT and return the user ID (sub).

    Raises jwt.PyJWTError subclasses on invalid/expired tokens, or ValueError
    if the token type doesn't match `expected_type`.
    """
    payload = jwt.decode(
        token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
    )
    if payload.get("type") != expected_type:
        raise ValueError(f"Expected token type '{expected_type}', got '{payload.get('type')}'")
    return payload["sub"]
