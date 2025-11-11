"""
Rate Limiter Utility
Prevents API rate limit errors by controlling request frequency
"""

import time
import logging
from functools import wraps
from config import Config

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, delay_seconds=None):
        """
        Initialize rate limiter
        
        Args:
            delay_seconds: Minimum seconds between calls (default from config)
        """
        self.delay = delay_seconds or Config.RATE_LIMIT_DELAY
        self.last_call_time = {}
    
    def wait_if_needed(self, key='default'):
        """
        Wait if needed to respect rate limits
        
        Args:
            key: Identifier for different rate limit buckets
        """
        current_time = time.time()
        
        if key in self.last_call_time:
            elapsed = current_time - self.last_call_time[key]
            if elapsed < self.delay:
                wait_time = self.delay - elapsed
                logger.debug(f"Rate limit: waiting {wait_time:.2f}s before next call")
                time.sleep(wait_time)
        
        self.last_call_time[key] = time.time()
    
    def __call__(self, func):
        """Decorator to apply rate limiting to a function"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.wait_if_needed(func.__name__)
            return func(*args, **kwargs)
        return wrapper


# Global rate limiter instance
_rate_limiter = RateLimiter()


def rate_limit(func):
    """
    Decorator to apply rate limiting to a function
    
    Usage:
        @rate_limit
        def my_api_call():
            # API call here
            pass
    """
    return _rate_limiter(func)


def wait_for_rate_limit(key='default'):
    """
    Manually wait for rate limit
    
    Args:
        key: Identifier for different rate limit buckets
    """
    _rate_limiter.wait_if_needed(key)
