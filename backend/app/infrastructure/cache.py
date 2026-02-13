"""
Redis cache service for CQRS query handlers.
Implements cache-aside pattern: check cache → miss → query DB → store in cache.
"""

import json
import logging
from functools import wraps
from typing import Any, Callable

from app.infrastructure.redis import redis_client

logger = logging.getLogger(__name__)

DEFAULT_TTL = 300  # 5 minutes


async def cache_get(key: str) -> Any | None:
    """Get a value from Redis cache."""
    try:
        data = await redis_client.get(key)
        if data:
            logger.debug(f"Cache HIT: {key}")
            return json.loads(data)
        logger.debug(f"Cache MISS: {key}")
    except Exception as e:
        logger.warning(f"Cache read error for {key}: {e}")
    return None


async def cache_set(key: str, value: Any, ttl: int = DEFAULT_TTL) -> None:
    """Store a value in Redis cache with TTL."""
    try:
        await redis_client.set(key, json.dumps(value, default=str), ex=ttl)
    except Exception as e:
        logger.warning(f"Cache write error for {key}: {e}")


async def cache_delete(pattern: str) -> None:
    """Delete cache entries matching a pattern."""
    try:
        keys = []
        async for key in redis_client.scan_iter(match=pattern):
            keys.append(key)
        if keys:
            await redis_client.delete(*keys)
            logger.info(f"Cache invalidated: {len(keys)} keys matching {pattern}")
    except Exception as e:
        logger.warning(f"Cache delete error for {pattern}: {e}")


def cached(prefix: str, ttl: int = DEFAULT_TTL):
    """Decorator that caches the result of an async query handler."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key from function name and arguments
            key_parts = [prefix]
            for arg in args:
                key_parts.append(str(arg))
            for k, v in sorted(kwargs.items()):
                key_parts.append(f"{k}={v}")
            cache_key = ":".join(key_parts)

            # Check cache
            result = await cache_get(cache_key)
            if result is not None:
                return result

            # Execute query
            result = await func(*args, **kwargs)

            # Store in cache
            if result is not None:
                await cache_set(cache_key, result, ttl)

            return result
        return wrapper
    return decorator
