"""app/auth/router.py — Auth endpoints: register, login, refresh, and forgot password."""
from __future__ import annotations

import random

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.security import (
    create_token_pair,
    decode_token,
    hash_password,
    verify_password,
)
from app.db.database import get_db
from app.models.user import User
from app.services.email import send_otp_email
from app.schemas.auth import (
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    ResetPasswordRequest,
    ResetPasswordResponse,
    TokenResponse,
    VerifyOtpRequest,
    VerifyOtpResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

_otp_store: dict[str, str] = {}
_verified_otps: set[str] = set()

_WRONG_CREDENTIALS = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Incorrect email or password",
)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Register a new user and return a token pair."""
    email_lower = body.email.lower()
    if db.query(User).filter(func.lower(User.email) == email_lower).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = User(
        name=body.name,
        email=email_lower,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(**create_token_pair(user.id))


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate and return a token pair.

    Deliberately returns the same error message for a wrong password or
    a nonexistent email — avoids leaking which emails are registered.
    """
    email_lower = body.email.lower()
    user = db.query(User).filter(func.lower(User.email) == email_lower).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise _WRONG_CREDENTIALS
    return TokenResponse(**create_token_pair(user.id))


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)) -> ForgotPasswordResponse:
    """Generate an OTP for an existing user email address and send via email."""
    email_lower = body.email.lower()
    user = db.query(User).filter(func.lower(User.email) == email_lower).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email does not exist",
        )

    otp = f"{random.randint(100000, 999999)}"
    _otp_store[email_lower] = otp
    _verified_otps.discard(email_lower)
    send_otp_email(email_lower, otp)
    return ForgotPasswordResponse(message="OTP generated successfully")


@router.post("/verify-otp", response_model=VerifyOtpResponse)
def verify_otp(body: VerifyOtpRequest) -> VerifyOtpResponse:
    """Verify an OTP that was previously generated for an existing email."""
    email_lower = body.email.lower()
    stored_otp = _otp_store.get(email_lower)
    if not stored_otp or stored_otp != body.otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    _verified_otps.add(email_lower)
    return VerifyOtpResponse(message="OTP verified successfully")


@router.post("/reset-password", response_model=ResetPasswordResponse)
def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)) -> ResetPasswordResponse:
    """Reset a user's password after OTP verification."""
    email_lower = body.email.lower()
    if email_lower not in _verified_otps:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OTP not verified")

    stored_otp = _otp_store.get(email_lower)
    if stored_otp and stored_otp != body.otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    user = db.query(User).filter(func.lower(User.email) == email_lower).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email does not exist")

    user.password_hash = hash_password(body.new_password)
    db.commit()
    _otp_store.pop(email_lower, None)
    _verified_otps.discard(email_lower)
    return ResetPasswordResponse(message="Password updated successfully")


@router.post("/refresh", response_model=TokenResponse)
def refresh(body: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Exchange a valid refresh token for a brand-new token pair (rotation)."""
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    try:
        user_id = decode_token(body.refresh_token, expected_type="refresh")
    except (jwt.PyJWTError, ValueError):
        raise exc

    user = db.get(User, user_id)
    if user is None:
        raise exc
    return TokenResponse(**create_token_pair(user.id))
