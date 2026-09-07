import hashlib
import json
import logging
import socket
from typing import Any, Dict, Optional
import redis.asyncio as redis


from app.config import settings

logger = logging.getLogger(__name__)
MAX_CACHE_VALUE_BYTES = 8 * 1024 * 1024

SOCKET_KEEPALIVE_OPTIONS = {}
tcp_keepidle = getattr(socket, "TCP_KEEPIDLE", None)
if tcp_keepidle is not None:
    SOCKET_KEEPALIVE_OPTIONS[tcp_keepidle] = 30

# Cache metrics for monitoring performance
class CacheMetrics:
    """Track cache hit/miss statistics."""
    hits: int = 0
    misses: int = 0
    errors: int = 0

    @classmethod
    def record_hit(cls) -> None:
        cls.hits += 1

    @classmethod
    def record_miss(cls) -> None:
        cls.misses += 1

    @classmethod
    def record_error(cls) -> None:
        cls.errors += 1

    @classmethod
    def get_stats(cls) -> Dict[str, int]:
        """Return current cache statistics."""
        total = cls.hits + cls.misses
        hit_rate = (cls.hits / total * 100) if total > 0 else 0
        return {
            "hits": cls.hits,
            "misses": cls.misses,
            "errors": cls.errors,
            "total": total,
            "hit_rate_percent": round(hit_rate, 2),
        }

    @classmethod
    def reset(cls) -> None:
        """Reset statistics for testing."""
        cls.hits = 0
        cls.misses = 0
        cls.errors = 0


# Initialize connection pool with production-ready settings
pool = redis.ConnectionPool.from_url(
    settings.REDIS_URL.get_secret_value(),
    decode_responses=True,
    max_connections=20,
    socket_connect_timeout=5,
    socket_keepalive=True,
    socket_keepalive_options=SOCKET_KEEPALIVE_OPTIONS,
)

redis_client = redis.Redis(connection_pool=pool)


async def reconnect_redis() -> None:
    """Drop stale pooled connections so the next command reconnects cleanly."""
    await pool.disconnect(inuse_connections=False)


def create_cache_key(*values: str) -> str:
    """Generates a stable, unique hashed Redis key from string parameters."""
    raw = "|".join(values)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    owner = values[0] if values else "global"
    return f"multimodal:{owner}:{digest}"


async def get_cache(key: str) -> Optional[Dict[str, Any]]:
    """Fetches and decodes data from cache. Fails gracefully if Redis is down."""
    try:
        value = await redis_client.get(key)
        if value is None:
            CacheMetrics.record_miss()
            return None
        CacheMetrics.record_hit()
        return json.loads(value)
    except redis.RedisError as e:
        logger.warning(f"Redis get connection failed; reconnecting for key {key}: {e}")
        try:
            await reconnect_redis()
            value = await redis_client.get(key)
            if value is None:
                CacheMetrics.record_miss()
                return None
            CacheMetrics.record_hit()
            return json.loads(value)
        except redis.RedisError as retry_error:
            logger.error(f"Redis get retry failed for key {key}: {retry_error}")
            CacheMetrics.record_error()
            return None


async def set_cache(key: str, value: Dict[str, Any], ttl: int = 3600) -> bool:
    """Stores serialized data with one retry for stale pooled connections."""
    serialized_value = json.dumps(value)
    if len(serialized_value.encode("utf-8")) > MAX_CACHE_VALUE_BYTES:
        logger.info("Skipping oversized Redis cache value for key %s", key)
        return False
    try:
        await redis_client.setex(key, ttl, serialized_value)
        return True
    except redis.RedisError as e:
        logger.warning(f"Redis set connection failed; reconnecting for key {key}: {e}")
        try:
            await reconnect_redis()
            await redis_client.setex(key, ttl, serialized_value)
            return True
        except redis.RedisError as retry_error:
            logger.error(f"Redis set retry failed for key {key}: {retry_error}")
            CacheMetrics.record_error()
            return False


async def invalidate_cache_pattern(pattern: str) -> int:
    """Delete all cache keys matching a pattern (e.g., 'multimodal:*')."""
    try:
        keys = await redis_client.keys(pattern)
        if not keys:
            return 0
        deleted = await redis_client.delete(*keys)
        logger.info(f"Invalidated {deleted} cache keys matching pattern '{pattern}'")
        return deleted
    except redis.RedisError as e:
        logger.error(f"Redis invalidation failed for pattern '{pattern}': {e}")
        return 0


async def check_redis_health() -> bool:
    """Health check for Redis connectivity."""
    try:
        pong = await redis_client.ping()
        return pong is True
    except redis.RedisError as e:
        logger.error(f"Redis health check failed: {e}")
        return False


async def close_redis() -> None:
    """Gracefully close Redis connection pool on app shutdown."""
    try:
        await redis_client.close()
        logger.info("Redis connection pool closed")
    except Exception as e:
        logger.error(f"Error closing Redis connection: {e}")
