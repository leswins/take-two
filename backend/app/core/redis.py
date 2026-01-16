"""
Redis client configuration for Upstash and local Redis.
Supports both redis:// and rediss:// (TLS) protocols.
"""

import redis
from typing import Optional
from functools import lru_cache
from app.core.config import settings


@lru_cache()
def get_redis_client() -> Optional[redis.Redis]:
    """
    Get a Redis client instance.
    Returns None if Redis is not configured or unavailable.
    """
    if not settings.REDIS_URL:
        return None

    try:
        # Upstash uses rediss:// (TLS), local Redis uses redis://
        client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5,
            retry_on_timeout=True,
        )
        # Test connection
        client.ping()
        return client
    except Exception as e:
        print(f"Redis connection failed: {e}")
        return None


def check_redis_connection() -> bool:
    """Health check for Redis connectivity."""
    client = get_redis_client()
    if client is None:
        return False
    try:
        return client.ping()
    except Exception:
        return False


# Optional: Simple caching helpers
def cache_get(key: str) -> Optional[str]:
    """Get value from cache."""
    client = get_redis_client()
    if client is None:
        return None
    try:
        return client.get(key)
    except Exception:
        return None


def cache_set(key: str, value: str, ttl_seconds: int = 3600) -> bool:
    """Set value in cache with TTL."""
    client = get_redis_client()
    if client is None:
        return False
    try:
        client.setex(key, ttl_seconds, value)
        return True
    except Exception:
        return False


def cache_delete(key: str) -> bool:
    """Delete value from cache."""
    client = get_redis_client()
    if client is None:
        return False
    try:
        client.delete(key)
        return True
    except Exception:
        return False
