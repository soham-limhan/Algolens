"""
app/routers/forum.py — Forum endpoints: threads, replies, and upvotes with Redis caching.
"""
from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.config import settings
from app.db.database import get_db
from app.models.forum import ForumLike, ForumReply, ForumThread
from app.models.user import User
from app.schemas.forum import (
    ForumReplyCreate,
    ForumReplyResponse,
    ForumThreadCreate,
    ForumThreadDetailResponse,
    ForumThreadResponse,
    UserMentionResponse,
)
from app.services.cache import cache_service

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


@router.get("/users/mentions", response_model=List[UserMentionResponse])
def search_users_for_mention(
    q: str = Query("", max_length=50),
    db: Session = Depends(get_db),
) -> List[UserMentionResponse]:
    """Search users by name for @mentions in forum threads and replies with caching."""
    clean_q = q.strip().lower()
    cache_key = f"forum:mentions:{clean_q}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return [UserMentionResponse.model_validate(u) for u in cached]

    query = db.query(User)
    if clean_q:
        term = f"%{clean_q}%"
        query = query.filter(func.lower(User.name).like(term))
    users = query.order_by(User.name).limit(10).all()
    results = [UserMentionResponse(id=u.id, name=u.name) for u in users]
    cache_service.set(cache_key, [r.model_dump() for r in results], ttl=300)
    return results


@router.get("/threads", response_model=List[ForumThreadResponse])
def list_threads(
    category: str = "All",
    search: str = "",
    sort_by: str = "newest",
    db: Session = Depends(get_db),
) -> List[ForumThreadResponse]:
    """List forum threads with optional category filter, search query, sorting, and Redis caching."""
    cat_clean = category.strip().lower()
    search_clean = search.strip().lower()
    sort_clean = sort_by.strip().lower()
    cache_key = f"forum:threads:{cat_clean}:{search_clean}:{sort_clean}"

    cached = cache_service.get(cache_key)
    if cached is not None:
        return [ForumThreadResponse.model_validate(t) for t in cached]

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

    cache_service.set(
        cache_key,
        [r.model_dump() for r in responses],
        ttl=settings.cache_ttl_forum_threads,
    )
    return responses


@router.get("/threads/{thread_id}", response_model=ForumThreadDetailResponse)
def get_thread(thread_id: str, db: Session = Depends(get_db)) -> ForumThreadDetailResponse:
    """Get a single thread detail with full replies list with Redis caching."""
    _validate_uuid(thread_id, "thread_id")
    cache_key = f"forum:thread:{thread_id}"
    cached = cache_service.get(cache_key)
    if cached is not None:
        return ForumThreadDetailResponse.model_validate(cached)

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
            parent_id=r.parent_id,
            parent_author=r.parent.author.name if (r.parent and r.parent.author) else None,
        )
        for r in thread.replies
    ]

    detail = ForumThreadDetailResponse(
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

    cache_service.set(
        cache_key,
        detail.model_dump(),
        ttl=settings.cache_ttl_forum_detail,
    )
    return detail


@router.post("/threads", response_model=ForumThreadResponse, status_code=status.HTTP_201_CREATED)
def create_thread(
    body: ForumThreadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ForumThreadResponse:
    """Create a new topic thread and invalidate forum thread listings cache."""
    thread = ForumThread(
        title=body.title,
        category=body.category,
        content=body.content,
        user_id=current_user.id,
    )
    db.add(thread)
    db.commit()
    db.refresh(thread)

    # Invalidate forum thread listings
    cache_service.delete_pattern("forum:threads:*")

    return _build_thread_response(thread)


@router.post("/threads/{thread_id}/like", response_model=ForumThreadResponse)
def toggle_like(
    thread_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ForumThreadResponse:
    """Toggle upvote/like on a thread for the authenticated user and invalidate caches."""
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

    # Invalidate cache for this thread and forum listings
    cache_service.delete(f"forum:thread:{thread_id}")
    cache_service.delete_pattern("forum:threads:*")

    return _build_thread_response(thread)


@router.post("/threads/{thread_id}/replies", response_model=ForumReplyResponse, status_code=status.HTTP_201_CREATED)
def add_reply(
    thread_id: str,
    body: ForumReplyCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ForumReplyResponse:
    """Post a reply to a thread or reply to another reply and invalidate caches."""
    _validate_uuid(thread_id, "thread_id")
    thread = db.get(ForumThread, thread_id)
    if thread is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found")

    parent_reply = None
    if body.parent_id:
        _validate_uuid(body.parent_id, "parent_id")
        parent_reply = db.get(ForumReply, body.parent_id)
        if parent_reply is None or parent_reply.thread_id != thread_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent reply not found on this thread",
            )

    reply = ForumReply(
        thread_id=thread_id,
        user_id=current_user.id,
        parent_id=body.parent_id,
        content=body.content,
    )
    db.add(reply)
    db.commit()
    db.refresh(reply)

    # Invalidate thread details and thread counts in listings
    cache_service.delete(f"forum:thread:{thread_id}")
    cache_service.delete_pattern("forum:threads:*")

    return ForumReplyResponse(
        id=reply.id,
        author=current_user.name,
        user_id=current_user.id,
        content=reply.content,
        created_at=reply.created_at,
        parent_id=reply.parent_id,
        parent_author=parent_reply.author.name if (parent_reply and parent_reply.author) else None,
    )

