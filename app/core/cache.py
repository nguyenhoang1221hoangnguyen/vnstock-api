"""
In-memory cache với TTL (Time To Live) cho VNStock API
"""
import time
from typing import Any, Optional, Dict
from threading import Lock
import hashlib
import json


class CacheEntry:
    """Đối tượng cache entry với TTL"""

    def __init__(self, value: Any, ttl: int):
        """
        Args:
            value: Giá trị cần cache
            ttl: Time to live (seconds)
        """
        self.value = value
        self.expiry_time = time.time() + ttl

    def is_expired(self) -> bool:
        """Kiểm tra entry đã hết hạn chưa"""
        return time.time() > self.expiry_time


class InMemoryCache:
    """
    Simple in-memory cache với TTL
    Thread-safe với locking
    """

    def __init__(self, default_ttl: int = 300):
        """
        Args:
            default_ttl: TTL mặc định (seconds), default 5 phút
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()
        self.default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    def _generate_key(self, *args, **kwargs) -> str:
        """
        Tạo cache key từ arguments

        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Cache key string
        """
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """
        Lấy giá trị từ cache

        Args:
            key: Cache key

        Returns:
            Giá trị nếu tồn tại và chưa hết hạn, None nếu không
        """
        with self._lock:
            entry = self._cache.get(key)

            if entry is None:
                self._misses += 1
                return None

            if entry.is_expired():
                del self._cache[key]
                self._misses += 1
                return None

            self._hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Lưu giá trị vào cache

        Args:
            key: Cache key
            value: Giá trị cần cache
            ttl: Time to live (seconds), nếu None sẽ dùng default_ttl
        """
        if ttl is None:
            ttl = self.default_ttl

        with self._lock:
            self._cache[key] = CacheEntry(value, ttl)

    def delete(self, key: str) -> bool:
        """
        Xóa entry khỏi cache

        Args:
            key: Cache key

        Returns:
            True nếu xóa thành công, False nếu key không tồn tại
        """
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self) -> None:
        """Xóa toàn bộ cache"""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0

    def cleanup_expired(self) -> int:
        """
        Dọn dẹp các entries đã hết hạn

        Returns:
            Số lượng entries đã bị xóa
        """
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]

            for key in expired_keys:
                del self._cache[key]

            return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """
        Lấy thống kê cache

        Returns:
            Dictionary chứa thống kê cache
        """
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

            return {
                'size': len(self._cache),
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate': round(hit_rate, 2),
                'total_requests': total_requests
            }

    def cache_result(self, ttl: Optional[int] = None):
        """
        Decorator để cache kết quả của function

        Args:
            ttl: Time to live (seconds)

        Returns:
            Decorated function

        Usage:
            @cache.cache_result(ttl=300)
            def expensive_function(param1, param2):
                return result
        """
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Tạo cache key từ function name và arguments
                cache_key = f"{func.__name__}:{self._generate_key(*args, **kwargs)}"

                # Thử lấy từ cache
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value

                # Nếu không có trong cache, thực thi function
                result = func(*args, **kwargs)

                # Lưu vào cache
                self.set(cache_key, result, ttl)

                return result

            return wrapper
        return decorator


# Global cache instance
_global_cache = InMemoryCache(default_ttl=300)  # 5 phút


def get_cache() -> InMemoryCache:
    """
    Lấy global cache instance

    Returns:
        InMemoryCache instance
    """
    return _global_cache
