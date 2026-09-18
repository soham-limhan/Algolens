"""
app/models/forum.py — SQLAlchemy models for forum threads, replies, and upvotes.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def _uuid_str() -> str:
    return str(uuid.uuid4())


class ForumThread(Base):
    __tablename__ = "forum_threads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    # Relationships
    author: Mapped["User"] = relationship("User")  # noqa: F821
    replies: Mapped[List["ForumReply"]] = relationship(
        "ForumReply", back_populates="thread", cascade="all, delete-orphan", order_by="ForumReply.created_at"
    )
    likes: Mapped[List["ForumLike"]] = relationship(
        "ForumLike", back_populates="thread", cascade="all, delete-orphan"
    )


class ForumReply(Base):
    __tablename__ = "forum_replies"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    thread_id: Mapped[str] = mapped_column(String(36), ForeignKey("forum_threads.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    parent_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("forum_replies.id"), nullable=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    # Relationships
    author: Mapped["User"] = relationship("User")  # noqa: F821
    thread: Mapped["ForumThread"] = relationship("ForumThread", back_populates="replies")
    parent: Mapped[Optional["ForumReply"]] = relationship(
        "ForumReply", remote_side="ForumReply.id", back_populates="children"
    )
    children: Mapped[List["ForumReply"]] = relationship(
        "ForumReply", back_populates="parent", cascade="all, delete-orphan", order_by="ForumReply.created_at"
    )


class ForumLike(Base):
    __tablename__ = "forum_likes"
    __table_args__ = (UniqueConstraint("thread_id", "user_id", name="uq_thread_user_like"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid_str)
    thread_id: Mapped[str] = mapped_column(String(36), ForeignKey("forum_threads.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)

    # Relationships
    thread: Mapped["ForumThread"] = relationship("ForumThread", back_populates="likes")
