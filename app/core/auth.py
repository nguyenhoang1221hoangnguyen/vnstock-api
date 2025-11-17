"""
API Key Authentication System
"""
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader
from sqlalchemy.orm import Session

# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class RateLimiter:
    """Simple in-memory rate limiter"""

    def __init__(self):
        self.requests: Dict[str, List[datetime]] = {}

    def check_rate_limit(
        self,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> bool:
        """
        Check if request is within rate limit

        Args:
            key: API key or IP address
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds

        Returns:
            True if allowed, False if rate limit exceeded
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)

        # Clean old requests
        if key in self.requests:
            self.requests[key] = [
                req_time for req_time in self.requests[key]
                if req_time > cutoff
            ]
        else:
            self.requests[key] = []

        # Check limit
        if len(self.requests[key]) >= max_requests:
            return False

        # Add current request
        self.requests[key].append(now)
        return True

    def get_remaining_requests(
        self,
        key: str,
        max_requests: int = 100,
        window_seconds: int = 60
    ) -> int:
        """Get number of remaining requests"""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)

        if key not in self.requests:
            return max_requests

        recent_requests = [
            req_time for req_time in self.requests[key]
            if req_time > cutoff
        ]

        return max(0, max_requests - len(recent_requests))


# Global rate limiter instance
rate_limiter = RateLimiter()


class APIKeyManager:
    """Manage API keys"""

    # In-memory API keys store (should be moved to database in production)
    _api_keys: Dict[str, Dict] = {
        # Default development key
        "dev_key_12345": {
            "name": "Development Key",
            "tier": "free",
            "max_requests_per_minute": 60,
            "max_requests_per_day": 1000,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True
        }
    }

    @classmethod
    def generate_api_key(cls, prefix: str = "vnsk") -> str:
        """Generate a secure API key"""
        random_part = secrets.token_urlsafe(32)
        return f"{prefix}_{random_part}"

    @classmethod
    def hash_api_key(cls, api_key: str) -> str:
        """Hash API key for storage"""
        return hashlib.sha256(api_key.encode()).hexdigest()

    @classmethod
    def create_api_key(
        cls,
        name: str,
        tier: str = "free",
        max_requests_per_minute: int = 60,
        max_requests_per_day: int = 1000
    ) -> str:
        """
        Create new API key

        Args:
            name: Name/description for the key
            tier: Tier (free, basic, pro, enterprise)
            max_requests_per_minute: Rate limit per minute
            max_requests_per_day: Rate limit per day

        Returns:
            Generated API key
        """
        api_key = cls.generate_api_key()

        cls._api_keys[api_key] = {
            "name": name,
            "tier": tier,
            "max_requests_per_minute": max_requests_per_minute,
            "max_requests_per_day": max_requests_per_day,
            "created_at": datetime.utcnow().isoformat(),
            "is_active": True,
            "total_requests": 0,
            "last_used": None
        }

        return api_key

    @classmethod
    def validate_api_key(cls, api_key: str) -> Optional[Dict]:
        """
        Validate API key

        Returns:
            API key info if valid, None if invalid
        """
        if not api_key:
            return None

        key_info = cls._api_keys.get(api_key)

        if not key_info:
            return None

        if not key_info.get("is_active", False):
            return None

        return key_info

    @classmethod
    def revoke_api_key(cls, api_key: str) -> bool:
        """Revoke an API key"""
        if api_key in cls._api_keys:
            cls._api_keys[api_key]["is_active"] = False
            return True
        return False

    @classmethod
    def get_all_keys(cls) -> List[Dict]:
        """Get all API keys (for admin)"""
        return [
            {
                "key": key[:20] + "...",  # Mask key
                **info
            }
            for key, info in cls._api_keys.items()
        ]

    @classmethod
    def update_usage(cls, api_key: str):
        """Update API key usage statistics"""
        if api_key in cls._api_keys:
            cls._api_keys[api_key]["total_requests"] = \
                cls._api_keys[api_key].get("total_requests", 0) + 1
            cls._api_keys[api_key]["last_used"] = datetime.utcnow().isoformat()


async def get_api_key(
    api_key: Optional[str] = Security(api_key_header)
) -> Optional[str]:
    """
    Dependency to get API key from header
    Optional - allows public endpoints without key
    """
    return api_key


async def require_api_key(
    api_key: Optional[str] = Security(api_key_header)
) -> str:
    """
    Dependency that requires valid API key
    Use for protected endpoints
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required. Get your key at /docs",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    # Validate API key
    key_info = APIKeyManager.validate_api_key(api_key)

    if not key_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or revoked API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    # Check rate limit
    max_per_minute = key_info.get("max_requests_per_minute", 60)

    if not rate_limiter.check_rate_limit(api_key, max_per_minute, 60):
        remaining = rate_limiter.get_remaining_requests(api_key, max_per_minute, 60)
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {max_per_minute} requests per minute.",
            headers={
                "X-RateLimit-Limit": str(max_per_minute),
                "X-RateLimit-Remaining": str(remaining),
                "X-RateLimit-Reset": "60"
            }
        )

    # Update usage statistics
    APIKeyManager.update_usage(api_key)

    return api_key


async def optional_api_key(
    api_key: Optional[str] = Security(api_key_header)
) -> Optional[Dict]:
    """
    Dependency for optional API key with rate limiting
    - With valid key: Higher rate limits
    - Without key: Lower rate limits (public tier)
    """
    if not api_key:
        # Public access with lower limits
        if not rate_limiter.check_rate_limit("public", max_requests=20, window_seconds=60):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Get an API key for higher limits at /docs",
                headers={
                    "X-RateLimit-Limit": "20",
                    "X-RateLimit-Remaining": "0"
                }
            )
        return {"tier": "public", "max_requests_per_minute": 20}

    # Validate key
    key_info = APIKeyManager.validate_api_key(api_key)

    if not key_info:
        # Invalid key - treat as public
        if not rate_limiter.check_rate_limit("public", max_requests=20, window_seconds=60):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Invalid API key. Treated as public tier with lower limits."
            )
        return {"tier": "public", "max_requests_per_minute": 20}

    # Valid key - check its rate limit
    max_per_minute = key_info.get("max_requests_per_minute", 60)

    if not rate_limiter.check_rate_limit(api_key, max_per_minute, 60):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Max {max_per_minute} requests per minute.",
            headers={
                "X-RateLimit-Limit": str(max_per_minute),
                "X-RateLimit-Remaining": "0"
            }
        )

    # Update usage
    APIKeyManager.update_usage(api_key)

    return key_info


# Tiers configuration
API_TIERS = {
    "public": {
        "name": "Public (No API Key)",
        "max_requests_per_minute": 20,
        "max_requests_per_day": 500,
        "features": ["basic_data", "technical_indicators"]
    },
    "free": {
        "name": "Free Tier",
        "max_requests_per_minute": 60,
        "max_requests_per_day": 1000,
        "features": ["basic_data", "technical_indicators", "fundamental_data", "screener"]
    },
    "basic": {
        "name": "Basic Tier",
        "max_requests_per_minute": 120,
        "max_requests_per_day": 5000,
        "features": ["*", "portfolio_analytics", "intraday_data"]
    },
    "pro": {
        "name": "Pro Tier",
        "max_requests_per_minute": 300,
        "max_requests_per_day": 20000,
        "features": ["*", "websocket", "priority_support"]
    },
    "enterprise": {
        "name": "Enterprise Tier",
        "max_requests_per_minute": 1000,
        "max_requests_per_day": 100000,
        "features": ["*", "custom_integration", "dedicated_support"]
    }
}
