"""
app/routers/forum.py — Forum endpoints: threads, replies, and upvotes.
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.database import get_db
from app.models.forum import ForumLike, ForumReply, ForumThread
from app.models.user import User
from app.schemas.forum import (
    ForumReplyCreate,
    ForumReplyResponse,
    ForumThreadCreate,
    ForumThreadDetailResponse,
    ForumThreadResponse,
)

router = APIRouter(prefix="/forum", tags=["forum"])


def _validate_uuid(val: str, field_name: str = "id") -> None:
    try:
        uuid.UUID(val)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=[{"field": field_name, "message": f"Invalid UUID format for {field_name}"}],
        )


def _build_thread_response(t: ForumThread) -> ForumThreadResponse:
    liked_by = [l.user_id for l in t.likes]
    author_name = t.author.name if t.author else "anonymous"
    return ForumThreadResponse(
        id=t.id,
        title=t.title,
        category=t.category,
        author=author_name,
        user_id=t.user_id,
        created_at=t.created_at,
        likes=len(liked_by),
        liked_by=liked_by,
        content=t.content,
        replies_count=len(t.replies),
    )


@router.get("/threads", response_model=List[ForumThreadResponse])
def list_threads(
    category: str = "All",
    search: str = "",
    sort_by: str = "newest",
    db: Session = Depends(get_db),
) -> List[ForumThreadResponse]:
    """List forum threads with optional category filter, search query, and sorting."""
    query = db.query(ForumThread)

    if category and category.lower() != "all":
        query = query.filter(func.lower(ForumThread.category) == category.lower())

    if search and search.strip():
        term = f"%{search.strip().lower()}%"
        query = query.filter(
            func.lower(ForumThread.title).like(term) | func.lower(ForumThread.content).like(term)
        )

    threads = query.all()

    # Build responses
    responses = [_build_thread_response(t) for t in threads]

    # Sorting
    if sort_by == "popular":
        responses.sort(key=lambda x: (x.likes, x.created_at), reverse=True)
    else:
        responses.sort(key=lambda x: x.created_at, reverse=True)

    return responses


@router.get("/threads/{thread_id}", response_model=ForumThreadDetailResponse)
def get_thread(thread_id: str, db: Session = Depends(get_db)) -> ForumThreadDetailResponse:
    """Get a single thread detail with full replies list."""
    _validate_uuid(thread_id, "thread_id")
    thread = db.get(ForumThread, thread_id)
    if thread is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")

    liked_by = [l.user_id for l in thread.likes]
    author_name = thread.author.name if thread.author else "anonymous"

    replies_resp = [
        ForumReplyResponse(
            id=r.id,
            author=r.author.name if r.author else "anonymous",
            user_id=r.user_id,
            content=r.content,
            created_at=r.created_at,
        )
        for r in thread.replies
    ]

    return ForumThreadDetailResponse(
        id=thread.id,
        title=thread.title,
        category=thread.category,
        author=author_name,
        user_id=thread.user_id,
        created_at=thread.created_at,
        likes=len(liked_by),
        liked_by=liked_by,
        content=thread.content,
        replies=replies_resp,
    )


@router.post("/threads", response_model=ForumThreadResponse, status_code=status.HTTP_201_CREATED)
def create_thread(
    body: ForumThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ForumThreadResponse:
    """Create a new topic thread."""
    thread = ForumThread(
        title=body.title,
        category=body.category,
        content=body.content,
        user_id=current_user.id,
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)
    return _build_thread_response(thread)


@router.post("/threads/{thread_id}/like", response_model=ForumThreadResponse)
def toggle_like(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ForumThreadResponse:
    """Toggle upvote/like on a thread for the authenticated user."""
    _validate_uuid(thread_id, "thread_id")
    thread = db.get(ForumThread, thread_id)
    if thread is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")

    existing_like = (
        db.query(ForumLike)
        .filter(ForumLike.thread_id == thread_id, ForumLike.user_id == current_user.id)
        .first()
    )

    if existing_like:
        db.delete(existing_like)
    else:
        db.add(ForumLike(thread_id=thread_id, user_id=current_user.id))

    db.commit()
    db.refresh(thread)
    return _build_thread_response(thread)


@router.post("/threads/{thread_id}/replies", response_model=ForumReplyResponse, status_code=status.HTTP_201_CREATED)
def add_reply(
    thread_id: str,
    body: ForumReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ForumReplyResponse:
    """Post a reply to a thread."""
    _validate_uuid(thread_id, "thread_id")
    thread = db.get(ForumThread, thread_id)
    if thread is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")

    reply = ForumReply(
        thread_id=thread_id,
        user_id=current_user.id,
        content=body.content,
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)

    return ForumReplyResponse(
        id=reply.id,
        author=current_user.name,
        user_id=current_user.id,
        content=reply.content,
        created_at=reply.created_at,
    )
