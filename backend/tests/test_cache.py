"""
tests/test_cache.py — Unit and integration tests for Redis caching layer and endpoints.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from pydantic import BaseModel

from app.main import app
from app.services.cache import CacheService, cache_service

client = TestClient(app)


class SampleModel(BaseModel):
    id: str
    count: int
    tags: list[str]


def test_cache_service_basic_operations():
    """Test standard get, set, delete operations in CacheService."""
    test_key = f"test:item:{uuid.uuid4()}"
    payload = {
        "title": "Two Sum",
        "tags": ["array", "hashmap"],
        "num": 42,
        "uuid": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Should be None initially
    assert cache_service.get(test_key) is None

    # Set and retrieve
    set_success = cache_service.set(test_key, payload, ttl=60)
    if cache_service.is_connected():
        assert set_success is True
        cached = cache_service.get(test_key)
        assert cached is not None
        assert cached["title"] == "Two Sum"
        assert cached["tags"] == ["array", "hashmap"]
        assert cached["num"] == 42

        # Delete
        del_success = cache_service.delete(test_key)
        assert del_success is True
        assert cache_service.get(test_key) is None


def test_cache_service_pydantic_serialization():
    """Test that Pydantic models serialize cleanly into Redis."""
    test_key = f"test:model:{uuid.uuid4()}"
    model_obj = SampleModel(id=str(uuid.uuid4()), count=10, tags=["dp", "tree"])

    if cache_service.is_connected():
        cache_service.set(test_key, model_obj, ttl=60)
        retrieved = cache_service.get(test_key)
        assert retrieved is not None
        assert retrieved["count"] == 10
        assert retrieved["tags"] == ["dp", "tree"]
        cache_service.delete(test_key)


def test_cache_service_delete_pattern():
    """Test wildcard/pattern invalidation with delete_pattern."""
    prefix = f"test:batch:{uuid.uuid4().hex[:8]}"
    if cache_service.is_connected():
        cache_service.set(f"{prefix}:1", {"val": 1}, ttl=60)
        cache_service.set(f"{prefix}:2", {"val": 2}, ttl=60)
        cache_service.set(f"{prefix}:3", {"val": 3}, ttl=60)

        assert cache_service.get(f"{prefix}:1") is not None
        assert cache_service.get(f"{prefix}:2") is not None

        deleted_count = cache_service.delete_pattern(f"{prefix}:*")
        assert deleted_count >= 3

        assert cache_service.get(f"{prefix}:1") is None
        assert cache_service.get(f"{prefix}:2") is None


def test_cache_service_disabled_mode():
    """Test that cache operations gracefully return None/False when disabled without throwing."""
    disabled_service = CacheService(enabled=False)
    assert not disabled_service.is_connected()
    assert disabled_service.get("any:key") is None
    assert disabled_service.set("any:key", {"a": 1}) is False
    assert disabled_service.delete("any:key") is False
    assert disabled_service.delete_pattern("any:*") == 0


def test_health_check_redis_status():
    """Verify GET /health includes redis status."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "redis" in data
    assert data["redis"] in ("connected", "disconnected")


def test_problems_endpoint_caching():
    """Verify GET /problems caches response."""
    # Clear problems cache first
    cache_service.delete_pattern("problems:*")

    res1 = client.get("/problems")
    assert res1.status_code == 200
    problems_data = res1.json()

    if cache_service.is_connected():
        cached_list = cache_service.get("problems:list")
        assert cached_list is not None
        assert len(cached_list) == len(problems_data)

        # Call again to exercise cache hit branch
        res2 = client.get("/problems")
        assert res2.status_code == 200
        assert res2.json() == problems_data
