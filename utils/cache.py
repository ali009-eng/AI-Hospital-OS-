"""
Caching utilities for performance optimization
"""
import functools
import hashlib
import json
import time
from typing import Any, Callable, Optional
import redis
from config import Config
import logging

logger = logging.getLogger(__name__)

# Try to connect to Redis, fallback to in-memory cache
try:
    if Config.REDIS_URL and Config.ENABLE_CACHING:
        redis_client = redis.from_url(Config.REDIS_URL, decode_responses=True)
        redis_client.ping()
        cache_type = "redis"
        logger.info("Using Redis cache")
    else:
        redis_client = None
        cache_type = "memory"
except Exception as e:
    logger.warning(f"Redis not available, using in-memory cache: {e}")
    redis_client = None
    cache_type = "memory"

# In-memory cache fallback
_memory_cache = {}
_cache_timestamps = {}


def get_cache_key(*args, **kwargs) -> str:
    """Generate cache key from function arguments"""
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    key_str = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_str.encode()).hexdigest()


def cache_result(ttl: int = None, key_prefix: str = ""):
    """
    Decorator to cache function results
    
    Args:
        ttl: Time to live in seconds (uses Config.CACHE_TTL if not provided)
        key_prefix: Prefix for cache keys
    """
    ttl = ttl or Config.CACHE_TTL
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if not Config.ENABLE_CACHING:
                return func(*args, **kwargs)
            
            cache_key = key_prefix + get_cache_key(*args, **kwargs)
            
            # Try to get from cache
            try:
                if cache_type == "redis" and redis_client:
                    cached = redis_client.get(cache_key)
                    if cached:
                        return json.loads(cached)
                else:
                    # In-memory cache
                    if cache_key in _memory_cache:
                        timestamp = _cache_timestamps.get(cache_key, 0)
                        if time.time() - timestamp < ttl:
                            return _memory_cache[cache_key]
            except Exception as e:
                logger.warning(f"Cache read error: {e}")
            
            # Compute result
            result = func(*args, **kwargs)
            
            # Store in cache
            try:
                if cache_type == "redis" and redis_client:
                    redis_client.setex(cache_key, ttl, json.dumps(result, default=str))
                else:
                    _memory_cache[cache_key] = result
                    _cache_timestamps[cache_key] = time.time()
                    
                    # Clean old entries from memory cache
                    if len(_memory_cache) > 1000:
                        oldest_key = min(_cache_timestamps.items(), key=lambda x: x[1])[0]
                        _memory_cache.pop(oldest_key, None)
                        _cache_timestamps.pop(oldest_key, None)
            except Exception as e:
                logger.warning(f"Cache write error: {e}")
            
            return result
        
        return wrapper
    return decorator


def clear_cache(key_pattern: str = None):
    """Clear cache entries"""
    try:
        if cache_type == "redis" and redis_client:
            if key_pattern:
                keys = redis_client.keys(key_pattern)
                if keys:
                    redis_client.delete(*keys)
            else:
                redis_client.flushdb()
        else:
            if key_pattern:
                # Simple pattern matching for memory cache
                keys_to_delete = [k for k in _memory_cache.keys() if key_pattern in k]
                for key in keys_to_delete:
                    _memory_cache.pop(key, None)
                    _cache_timestamps.pop(key, None)
            else:
                _memory_cache.clear()
                _cache_timestamps.clear()
    except Exception as e:
        logger.error(f"Cache clear error: {e}")

