"""
app/services/cache.py — Redis caching layer for AlgoLens.

Features:
- Thread-safe connection pool with connection and socket timeouts.
- Automatic JSON serialization and deserialization (handles UUIDs, datetimes, Pydantic models).
- Safe pattern-based cache invalidation using Redis scan_iter.
- Graceful degradation: never throws unhandled exceptions if Redis is down or unavailable.
"""
from __future__ import annotations

import json
import logging
from datetime import date, datetime
from typing import Any, Optional
from uuid import UUID

from app.config import settings

logger = logging.getLogger(__name__)


class CustomJSONEncoder(json.JSONEncoder):
    """Encodes custom types such as datetime, date, UUID, or Pydantic models."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if hasattr(obj, "model_dump"):
            return obj.model_dump()
        if hasattr(obj, "dict"):
            return obj.dict()
        return super().default(obj)


class CacheService:
    def __init__(self, redis_url: Optional[str] = None, enabled: Optional[bool] = None) -> None:
        self.url = redis_url or settings.redis_url
        self.enabled = settings.redis_enabled if enabled is None else enabled
        self._client: Optional[Any] = None
        self._init_client()

    def _init_client(self) -> None:
        if not self.enabled:
            logger.info("Redis cache is explicitly disabled.")
            return

        try:
            import redis
            self._client = redis.Redis.from_url(
                self.url,
                decode_responses=True,
                socket_timeout=2.0,
                socket_connect_timeout=2.0,
                retry_on_timeout=True,
            )
            # Test connection
            self._client.ping()
            logger.info("Redis cache successfully connected to %s", self.url)
        except Exception as e:
            logger.warning("Redis cache connection failed (%s). Operating in bypass mode.", e)
            self._client = None

    def is_connected(self) -> bool:
        """Returns True if Redis is reachable, False otherwise."""
        if not self.enabled or self._client is None:
            return False
        try:
            return bool(self._client.ping())
        except Exception:
            return False

    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve and deserialize a JSON-encoded value from cache.
        Returns None on cache miss, failure, or when disabled.
        """
        if not self.enabled or self._client is None:
            return None

        try:
            val = self._client.get(key)
            if val is None:
                return None
            return json.loads(val)
        except Exception as e:
            logger.debug("Cache get error for key '%s': %s", key, e)
            return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Serialize and store a value in cache with an optional TTL (in seconds).
        Returns True on success, False otherwise.
        """
        if not self.enabled or self._client is None:
            return False

        try:
            serialized = json.dumps(value, cls=CustomJSONEncoder)
            if ttl is not None and ttl > 0:
                self._client.set(key, serialized, ex=ttl)
            else:
                self._client.set(key, serialized)
            return True
        except Exception as e:
            logger.debug("Cache set error for key '%s': %s", key, e)
            return False

    def delete(self, key: str) -> bool:
        """Delete a single key from cache."""
        if not self.enabled or self._client is None:
            return False

        try:
            self._client.delete(key)
            return True
        except Exception as e:
            logger.debug("Cache delete error for key '%s': %s", key, e)
            return False

    def delete_pattern(self, pattern: str) -> int:
        """
        Find and delete all keys matching a glob pattern using non-blocking scan_iter.
        Returns number of deleted keys.
        """
        if not self.enabled or self._client is None:
            return 0

        try:
            deleted_count = 0
            keys_to_delete = []
            for k in self._client.scan_iter(match=pattern, count=100):
                keys_to_delete.append(k)
                if len(keys_to_delete) >= 500:
                    deleted_count += self._client.delete(*keys_to_delete)
                    keys_to_delete = []

            if keys_to_delete:
                deleted_count += self._client.delete(*keys_to_delete)

            return deleted_count
        except Exception as e:
            logger.debug("Cache delete_pattern error for pattern '%s': %s", pattern, e)
            return 0

    def flush_all(self) -> bool:
        """Flush current Redis database."""
        if not self.enabled or self._client is None:
            return False
        try:
            self._client.flushdb()
            return True
        except Exception as e:
            logger.debug("Cache flush error: %s", e)
            return False


# Global singleton instance
cache_service = CacheService()
