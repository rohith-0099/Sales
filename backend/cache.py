"""
Caching utilities for performance optimization.
Implements simple TTL-based caching for expensive operations.
"""

import time
from functools import wraps
from typing import Any, Callable, Dict, Tuple


class CacheEntry:
    """Simple cache entry with TTL support."""
    
    def __init__(self, value: Any, ttl_seconds: int = 300):
        self.value = value
        self.created_at = time.time()
        self.ttl_seconds = ttl_seconds
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return time.time() - self.created_at > self.ttl_seconds


def cached(ttl_seconds: int = 300, max_size: int = 128):
    """
    Decorator for caching function results with TTL.
    
    Args:
        ttl_seconds: Time to live in seconds (default: 5 minutes)
        max_size: Maximum cache size (default: 128 entries)
    """
    def decorator(func: Callable) -> Callable:
        cache: Dict[str, CacheEntry] = {}
        
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key from function arguments
            cache_key = str((args, frozenset(kwargs.items())))
            
            # Check if cached and not expired
            if cache_key in cache and not cache[cache_key].is_expired():
                return cache[cache_key].value
            
            # Limit cache size
            if len(cache) >= max_size:
                oldest_key = min(cache.keys(), key=lambda k: cache[k].created_at)
                del cache[oldest_key]
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache[cache_key] = CacheEntry(result, ttl_seconds)
            return result
        
        # Expose cache control methods
        wrapper.clear_cache = lambda: cache.clear()
        wrapper.cache_info = lambda: {"size": len(cache), "max_size": max_size}
        
        return wrapper
    
    return decorator
