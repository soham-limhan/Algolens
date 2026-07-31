"""
tests/test_forum.py — Endpoint & unit tests for Forum endpoints.
"""
from __future__ import annotations

import uuid
import pytest
from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_user
from app.main import app
from app.models.user import User

client = TestClient(app)

_TEST_USER_ID = str(uuid.uuid4())
_MOCK_USER = User(id=_TEST_USER_ID, name="Forum Tester", email="forum_tester@example.com", password_hash="hash")


@pytest.fixture(autouse=True)
def override_user():
    app.dependency_overrides[get_current_user] = lambda: _MOCK_USER
    yield
    app.dependency_overrides.pop(get_current_user, None)


def test_create_thread_and_get_detail():
    # 1. Create thread
    payload = {
        "title": "How to optimize Space Complexity?",
        "category": "Algorithms",
        "content": "What are the best tricks to reduce O(N^2) space to O(N) in DP?",
    }
    create_res = client.post("/forum/threads", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["title"] == payload["title"]
    assert created_data["category"] == "Algorithms"
    assert created_data["likes"] == 0
    thread_id = created_data["id"]

    # 2. Fetch detail
    detail_res = client.get(f"/forum/threads/{thread_id}")
    assert detail_res.status_code == 200
    detail_data = detail_res.json()
    assert detail_data["id"] == thread_id
    assert detail_data["replies"] == []

    # 3. Add reply
    reply_payload = {"content": "Use rolling array technique!"}
    reply_res = client.post(f"/forum/threads/{thread_id}/replies", json=reply_payload)
    assert reply_res.status_code == 201
    reply_data = reply_res.json()
    assert reply_data["content"] == reply_payload["content"]
    assert reply_data["author"] == "Forum Tester"

    # 4. Toggle Like
    like_res = client.post(f"/forum/threads/{thread_id}/like")
    assert like_res.status_code == 200
    like_data = like_res.json()
    assert like_data["likes"] == 1
    assert _TEST_USER_ID in like_data["liked_by"]

    # 5. Unlike
    unlike_res = client.post(f"/forum/threads/{thread_id}/like")
    assert unlike_res.status_code == 200
    assert unlike_res.json()["likes"] == 0


def test_list_threads_filtering_and_search():
    # Create thread under Questions category
    payload = {
        "title": "Segment tree vs Fenwick tree comparison",
        "category": "Questions",
        "content": "Which structure is easier to implement in competitive programming?",
    }
    client.post("/forum/threads", json=payload)

    # Filter by category
    res_cat = client.get("/forum/threads?category=Questions")
    assert res_cat.status_code == 200
    items = res_cat.json()
    assert any(t["title"] == payload["title"] for t in items)

    # Search query
    res_search = client.get("/forum/threads?search=Segment")
    assert res_search.status_code == 200
    search_items = res_search.json()
    assert any(t["title"] == payload["title"] for t in search_items)


def test_invalid_category_rejected():
    payload = {
        "title": "Invalid Category Topic",
        "category": "InvalidCategoryName",
        "content": "Some content",
    }
    res = client.post("/forum/threads", json=payload)
    assert res.status_code == 422
    assert res.json()["detail"][0]["field"] == "category"


def test_invalid_uuid_thread_detail_rejected():
    res = client.get("/forum/threads/not-a-valid-uuid")
    assert res.status_code == 422
    assert res.json()["detail"][0]["field"] == "thread_id"
