"""
Cache Manager Module

Manages caching of API responses to avoid redundant calls:
- In-memory caching with TTL
- File-based caching for persistence
- Cache decorator for easy implementation
"""

import hashlib
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional
from functools import wraps

class CacheManager:
    """Manage caching of API responses"""
    
    def __init__(self, cache_dir: Path = Path('data/cache'), 
                 cache_duration_hours: int = 6):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self._memory_cache = {}
    
    def _get_cache_key(self, *args, **kwargs) -> str:
        """Generate unique cache key from function arguments"""
        key_data = f"{args}{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache key"""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def get(self, func_name: str, *args, **kwargs) -> Optional[Any]:
        """Retrieve cached data if not expired"""
        cache_key = self._get_cache_key(func_name, *args, **kwargs)
        
        # Check memory cache first
        if cache_key in self._memory_cache:
            value, expiry = self._memory_cache[cache_key]
            if datetime.now() < expiry:
                print(f"💾 Memory cache HIT for {func_name}")
                return value
            else:
                del self._memory_cache[cache_key]
        
        # Check file cache
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            age = datetime.now() - datetime.fromtimestamp(cache_path.stat().st_mtime)
            if age < self.cache_duration:
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                print(f"💾 File cache HIT for {func_name}")
                return cached_data
            else:
                cache_path.unlink()
        
        print(f"💾 Cache MISS for {func_name}")
        return None
    
    def set(self, func_name: str, data: Any, *args, **kwargs) -> None:
        """Store data in cache"""
        cache_key = self._get_cache_key(func_name, *args, **kwargs)
        expiry = datetime.now() + self.cache_duration
        
        # Store in memory cache
        self._memory_cache[cache_key] = (data, expiry)
        
        # Store in file cache
        cache_path = self._get_cache_path(cache_key)
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)
        
        print(f"💾 Cached data for {func_name}")
    
    def clear(self, func_name: Optional[str] = None) -> int:
        """Clear cache for specific function or all"""
        count = 0
        
        # Clear memory cache
        if func_name:
            keys_to_delete = [k for k in self._memory_cache.keys() if k.startswith(func_name)]
            for key in keys_to_delete:
                del self._memory_cache[key]
                count += 1
        else:
            count = len(self._memory_cache)
            self._memory_cache.clear()
        
        # Clear file cache
        for cache_file in self.cache_dir.glob("*.pkl"):
            if func_name is None or cache_file.stem.startswith(func_name):
                cache_file.unlink()
                count += 1
        
        print(f"🗑️ Cleared {count} cache files")
        return count
    
    def cache_decorator(self, func):
        """Decorator for automatic caching"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = self._get_cache_key(func.__name__, *args, **kwargs)
            cached = self.get(func.__name__, *args, **kwargs)
            
            if cached is not None:
                return cached
            
            result = func(*args, **kwargs)
            self.set(func.__name__, result, *args, **kwargs)
            return result
        
        return wrapper