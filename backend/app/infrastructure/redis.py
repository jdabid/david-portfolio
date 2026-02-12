"""
Redis async client.
Used for response caching, rate limiting, and session storage.
"""

from redis.asyncio import Redis

from app.config import settings

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
