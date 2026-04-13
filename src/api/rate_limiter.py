"""Distributed rate limiting with Redis"""
from src.cache.redis_client import cache
import time
from typing import Optional, Tuple, Dict

class RateLimiter:
    """Token bucket algorithm for API rate limiting"""
    
    def __init__(self):
        self.limits = {
            "free": {"requests": 100, "window": 3600},      # 100/hour
            "individual": {"requests": 1000, "window": 3600}, # 1000/hour
            "professional": {"requests": 10000, "window": 3600}, # 10k/hour
            "enterprise": {"requests": 100000, "window": 3600}  # 100k/hour
        }
    
    def check_rate_limit(self, api_key: str, tier: str) -> Tuple[bool, Dict[str, int]]:
        """Check if request is within limits"""
        limit_config = self.limits.get(tier, self.limits["free"])
        # Use floor division for consistent windows
        window_id = int(time.time() / limit_config['window'])
        key = f"ratelimit:{api_key}:{window_id}"
        
        try:
            current = cache.client.incr(key)
            if current == 1:
                cache.client.expire(key, limit_config['window'])
            
            remaining = max(0, limit_config['requests'] - current)
            reset_at = (window_id + 1) * limit_config['window']
            
            headers = {
                "X-RateLimit-Limit": limit_config['requests'],
                "X-RateLimit-Remaining": remaining,
                "X-RateLimit-Reset": reset_at
            }
            
            if current > limit_config['requests']:
                return False, headers
            
            return True, headers
        except Exception:
            # Fallback to allow request if Redis is down
            return True, {}

rate_limiter = RateLimiter()
