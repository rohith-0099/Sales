"""
Performance monitoring and request timing utilities.
"""

import time
import logging
from functools import wraps
from typing import Callable, Any

logger = logging.getLogger(__name__)


def log_timing(operation_name: str):
    """
    Decorator to log execution time of functions.
    
    Usage:
        @log_timing("database_query")
        def fetch_data():
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                logger.debug(f"{operation_name} completed in {elapsed:.3f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"{operation_name} failed after {elapsed:.3f}s: {str(e)}")
                raise
        
        return wrapper
    
    return decorator


class PerformanceMonitor:
    """Simple performance monitoring utility."""
    
    def __init__(self):
        self.metrics = {}
    
    def start_timer(self, name: str):
        """Start timing an operation."""
        self.metrics[name] = {"start": time.time()}
    
    def stop_timer(self, name: str) -> float:
        """Stop timing and return elapsed time."""
        if name not in self.metrics:
            logger.warning(f"Timer '{name}' was not started")
            return 0.0
        
        elapsed = time.time() - self.metrics[name]["start"]
        self.metrics[name]["elapsed"] = elapsed
        return elapsed
    
    def get_metrics(self) -> dict:
        """Get all recorded metrics."""
        return {k: v.get("elapsed", 0.0) for k, v in self.metrics.items()}
    
    def log_metrics(self):
        """Log all recorded metrics."""
        for name, elapsed in self.get_metrics().items():
            logger.info(f"{name}: {elapsed:.3f}s")
    
    def reset(self):
        """Reset all metrics."""
        self.metrics.clear()
