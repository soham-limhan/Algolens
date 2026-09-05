from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator



class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must not exceed 128 characters")
        return v

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 120:
            raise ValueError("Name must be between 1 and 120 characters")
        return v

    @field_validator("email")
    @classmethod
    def email_normalize(cls, v: str) -> str:
        v = v.strip().lower()
        if len(v) > 255:
            raise ValueError("Email must not exceed 255 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    password: str = Field(..., min_length=1)

    @field_validator("email")
    @classmethod
    def email_normalize(cls, v: str) -> str:
        return v.strip().lower()


class RefreshRequest(BaseModel):
    refresh_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)

    @field_validator("email")
    @classmethod
    def email_normalize(cls, v: str) -> str:
        return v.strip().lower()


class ForgotPasswordResponse(BaseModel):
    message: str


class VerifyOtpRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    otp: str = Field(..., min_length=6, max_length=6)

    @field_validator("email")
    @classmethod
    def email_normalize(cls, v: str) -> str:
        return v.strip().lower()


class VerifyOtpResponse(BaseModel):
    message: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr = Field(..., max_length=255)
    otp: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def email_normalize(cls, v: str) -> str:
        return v.strip().lower()

    @field_validator("new_password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must not exceed 128 characters")
        return v


class ResetPasswordResponse(BaseModel):
    message: str


class UserProfileResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: Optional[UserProfileResponse] = None



class UpdateProfileRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 120:
            raise ValueError("Name must be between 1 and 120 characters")
        return v


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("new_password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if len(v) > 128:
            raise ValueError("Password must not exceed 128 characters")
        return v


UserProfileResponse.model_rebuild()
TokenResponse.model_rebuild()


