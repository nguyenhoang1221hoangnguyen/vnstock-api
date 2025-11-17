"""
Admin API routes for managing system
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Body
from typing import Optional, Dict, Any
from datetime import datetime

from ..core.auth import (
    APIKeyManager,
    require_api_key,
    rate_limiter,
    API_TIERS
)

admin_router = APIRouter(prefix="/api/admin", tags=["Admin"])


@admin_router.post("/api-keys/create")
async def create_api_key(
    name: str = Body(..., description="Name/description for the API key"),
    tier: str = Body("free", description="Tier: free, basic, pro, enterprise"),
    admin_key: str = Depends(require_api_key)
):
    """
    Create a new API key (Admin only)

    **Requires admin API key**

    **Available tiers:**
    - `free`: 60 req/min, 1,000 req/day
    - `basic`: 120 req/min, 5,000 req/day
    - `pro`: 300 req/min, 20,000 req/day
    - `enterprise`: 1,000 req/min, 100,000 req/day
    """
    # Check if requester is admin (using default dev key for now)
    if admin_key != "dev_key_12345":
        raise HTTPException(status_code=403, detail="Admin access required")

    if tier not in API_TIERS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid tier. Available: {', '.join(API_TIERS.keys())}"
        )

    tier_config = API_TIERS[tier]

    api_key = APIKeyManager.create_api_key(
        name=name,
        tier=tier,
        max_requests_per_minute=tier_config["max_requests_per_minute"],
        max_requests_per_day=tier_config["max_requests_per_day"]
    )

    return {
        "success": True,
        "api_key": api_key,
        "tier": tier,
        "tier_config": tier_config,
        "message": "API key created successfully. Keep this key secret!",
        "usage": f"Add header: X-API-Key: {api_key}"
    }


@admin_router.get("/api-keys/list")
async def list_api_keys(
    admin_key: str = Depends(require_api_key)
):
    """
    List all API keys (Admin only)

    Shows masked keys for security
    """
    if admin_key != "dev_key_12345":
        raise HTTPException(status_code=403, detail="Admin access required")

    keys = APIKeyManager.get_all_keys()

    return {
        "success": True,
        "total": len(keys),
        "keys": keys
    }


@admin_router.post("/api-keys/revoke")
async def revoke_api_key(
    api_key: str = Body(..., description="API key to revoke"),
    admin_key: str = Depends(require_api_key)
):
    """
    Revoke an API key (Admin only)
    """
    if admin_key != "dev_key_12345":
        raise HTTPException(status_code=403, detail="Admin access required")

    success = APIKeyManager.revoke_api_key(api_key)

    if not success:
        raise HTTPException(status_code=404, detail="API key not found")

    return {
        "success": True,
        "message": f"API key revoked successfully"
    }


@admin_router.get("/api-keys/tiers")
async def get_tier_info():
    """
    Get information about available API tiers

    Public endpoint - no auth required
    """
    return {
        "success": True,
        "tiers": API_TIERS
    }


@admin_router.get("/rate-limit/status")
async def get_rate_limit_status(
    api_key: Optional[str] = Depends(require_api_key)
):
    """
    Get current rate limit status for your API key
    """
    key_info = APIKeyManager.validate_api_key(api_key)

    if not key_info:
        raise HTTPException(status_code=401, detail="Invalid API key")

    max_per_minute = key_info.get("max_requests_per_minute", 60)
    remaining = rate_limiter.get_remaining_requests(
        api_key,
        max_per_minute,
        60
    )

    return {
        "success": True,
        "api_key": api_key[:20] + "...",  # Masked
        "tier": key_info.get("tier", "free"),
        "rate_limits": {
            "requests_per_minute": {
                "limit": max_per_minute,
                "remaining": remaining,
                "used": max_per_minute - remaining
            },
            "requests_per_day": {
                "limit": key_info.get("max_requests_per_day", 1000),
                "used": key_info.get("total_requests", 0)
            }
        },
        "usage": {
            "total_requests": key_info.get("total_requests", 0),
            "last_used": key_info.get("last_used"),
            "created_at": key_info.get("created_at")
        }
    }


@admin_router.get("/system/health")
async def system_health():
    """
    Get system health status

    Public endpoint
    """
    return {
        "success": True,
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "operational",
            "database": "operational",
            "scheduler": "operational",
            "cache": "operational"
        }
    }


@admin_router.get("/system/stats")
async def system_stats(
    admin_key: str = Depends(require_api_key)
):
    """
    Get system statistics (Admin only)
    """
    if admin_key != "dev_key_12345":
        raise HTTPException(status_code=403, detail="Admin access required")

    # Count total API keys
    all_keys = APIKeyManager.get_all_keys()
    active_keys = [k for k in all_keys if k.get("is_active", False)]

    # Tier distribution
    tier_dist = {}
    for key in active_keys:
        tier = key.get("tier", "unknown")
        tier_dist[tier] = tier_dist.get(tier, 0) + 1

    # Total requests
    total_requests = sum(k.get("total_requests", 0) for k in all_keys)

    return {
        "success": True,
        "api_keys": {
            "total": len(all_keys),
            "active": len(active_keys),
            "revoked": len(all_keys) - len(active_keys),
            "by_tier": tier_dist
        },
        "usage": {
            "total_requests": total_requests,
            "requests_today": 0  # TODO: Implement daily tracking
        },
        "rate_limiter": {
            "active_keys_tracked": len(rate_limiter.requests)
        }
    }
