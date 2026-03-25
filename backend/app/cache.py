"""
Redis caching layer for TrendNexAI.
Handles all caching logic with TTL management and invalidation.
"""

import logging
import json
from typing import Optional, Any
from redis.asyncio import Redis
import os

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Cache TTL (Time To Live) in seconds
CACHE_TTL = {
    "articles_list": 60,      # 1 minute
    "article_detail": 300,    # 5 minutes
    "categories": 3600,       # 1 hour
    "trending": 600,          # 10 minutes
    "search": 300,            # 5 minutes
}

class CacheManager:
    """Manages Redis caching for the application"""
    
    _redis: Optional[Redis] = None
    
    @classmethod
    async def get_redis(cls) -> Redis:
        """Get or create Redis connection"""
        if cls._redis is None:
            cls._redis = await Redis.from_url(REDIS_URL, decode_responses=True)
        return cls._redis
    
    @classmethod
    async def close(cls):
        """Close Redis connection"""
        if cls._redis:
            await cls._redis.close()
            cls._redis = None
    
    @classmethod
    async def get(cls, key: str) -> Optional[Any]:
        """
        Retrieve cached value by key
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        try:
            redis = await cls.get_redis()
            cached = await redis.get(key)
            
            if cached:
                logger.debug(f"Cache HIT: {key}")
                try:
                    return json.loads(cached)
                except json.JSONDecodeError:
                    return cached
            
            logger.debug(f"Cache MISS: {key}")
            return None
        except Exception as e:
            logger.warning(f"Cache get error: {e}")
            return None
    
    @classmethod
    async def set(
        cls,
        key: str,
        value: Any,
        ttl: int = 300,
        cache_type: str = "default"
    ) -> bool:
        """
        Set cached value with TTL
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            cache_type: Type of cache (for default TTL lookup)
            
        Returns:
            True if successful
        """
        try:
            redis = await cls.get_redis()
            
            # Use cache_type TTL if ttl not specified
            if ttl == 300 and cache_type in CACHE_TTL:
                ttl = CACHE_TTL[cache_type]
            
            # Serialize value
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            # Set with expiration
            await redis.setex(key, ttl, value)
            logger.debug(f"Cache SET: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.warning(f"Cache set error: {e}")
            return False
    
    @classmethod
    async def delete(cls, *keys: str) -> int:
        """Delete one or more cache keys"""
        try:
            redis = await cls.get_redis()
            deleted = await redis.delete(*keys)
            logger.debug(f"Cache DELETE: {keys} ({deleted} keys)")
            return deleted
        except Exception as e:
            logger.warning(f"Cache delete error: {e}")
            return 0
    
    @classmethod
    async def delete_pattern(cls, pattern: str) -> int:
        """Delete all keys matching pattern"""
        try:
            redis = await cls.get_redis()
            keys = await redis.keys(pattern)
            
            if keys:
                deleted = await redis.delete(*keys)
                logger.debug(f"Cache DELETE PATTERN: {pattern} ({deleted} keys)")
                return deleted
            return 0
        except Exception as e:
            logger.warning(f"Cache delete pattern error: {e}")
            return 0
    
    @classmethod
    async def clear_articles(cls):
        """Clear all article-related caches"""
        patterns = [
            "articles:*",
            "article:*",
            "trending:*",
            "search:*",
        ]
        
        total_deleted = 0
        for pattern in patterns:
            total_deleted += await cls.delete_pattern(pattern)
        
        logger.info(f"Cleared article cache: {total_deleted} keys")
        return total_deleted
    
    @classmethod
    async def get_stats(cls) -> dict:
        """Get Redis cache statistics"""
        try:
            redis = await cls.get_redis()
            info = await redis.info()
            
            return {
                "memory_usage": info.get("used_memory_human", "N/A"),
                "connected_clients": info.get("connected_clients", 0),
                "total_commands": info.get("total_commands_processed", 0),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0) / 
                    (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1)) * 100
                    if (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0)) > 0
                    else 0
                ),
            }
        except Exception as e:
            logger.warning(f"Cache stats error: {e}")
            return {}


# Utility functions for common caching patterns

async def cache_get_or_set(
    key: str,
    fetch_func,
    ttl: int = 300,
    cache_type: str = "default"
):
    """
    Get from cache, or fetch and cache if not found
    
    Args:
        key: Cache key
        fetch_func: Async function to call if cache miss
        ttl: Time to live
        cache_type: Cache type for default TTL
        
    Returns:
        Cached or fetched value
    """
    # Try cache first
    cached = await CacheManager.get(key)
    if cached is not None:
        return cached
    
    # Cache miss - fetch and cache
    value = await fetch_func()
    await CacheManager.set(key, value, ttl, cache_type)
    
    return value


async def init_cache():
    """Initialize cache connection on startup"""
    try:
        redis = await CacheManager.get_redis()
        await redis.ping()
        logger.info("✓ Redis cache connected")
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        raise
