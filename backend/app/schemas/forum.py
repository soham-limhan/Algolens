"""
app/schemas/forum.py — Pydantic models for forum endpoints.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

ALLOWED_CATEGORIES = {"General", "Algorithms", "Questions", "Contest", "Feedback"}


class ForumThreadCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=50)
    content: str = Field(..., min_length=1, max_length=10000)

    @field_validator("title")
    @classmethod
    def validate_title(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed or len(trimmed) > 200:
            raise ValueError("Title must be between 1 and 200 characters")
        return trimmed

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        cat = v.strip().capitalize()
        # Find exact case match in allowed set if possible
        for allowed in ALLOWED_CATEGORIES:
            if allowed.lower() == v.strip().lower():
                return allowed
        raise ValueError(f"Category must be one of: {', '.join(sorted(ALLOWED_CATEGORIES))}")

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed or len(trimmed) > 10000:
            raise ValueError("Content must be between 1 and 10,000 characters")
        return trimmed


class ForumReplyCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000)
    parent_id: Optional[str] = None

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        trimmed = v.strip()
        if not trimmed or len(trimmed) > 5000:
            raise ValueError("Reply content must be between 1 and 5,000 characters")
        return trimmed


class ForumReplyResponse(BaseModel):
    id: str
    author: str
    user_id: str
    content: str
    created_at: datetime
    parent_id: Optional[str] = None
    parent_author: Optional[str] = None

    model_config = {"from_attributes": True}


class UserMentionResponse(BaseModel):
    id: str
    name: str

    model_config = {"from_attributes": True}


class ForumThreadResponse(BaseModel):
    id: str
    title: str
    category: str
    author: str
    user_id: str
    created_at: datetime
    likes: int
    liked_by: List[str]
    content: str
    replies_count: int

    model_config = {"from_attributes": True}


class ForumThreadDetailResponse(BaseModel):
    id: str
    title: str
    category: str
    author: str
    user_id: str
    created_at: datetime
    likes: int
    liked_by: List[str]
    content: str
    replies: List[ForumReplyResponse]

    model_config = {"from_attributes": True}
