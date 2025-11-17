# 🔐 Authentication & API Keys Guide

## Overview

VNStock API sử dụng **API Key Authentication** để bảo vệ resources và implement rate limiting công bằng cho tất cả users.

## 🎯 API Tiers

### Public Tier (Không cần API Key)
- ⚡ **Rate Limit**: 20 requests/minute
- 📊 **Daily Limit**: 500 requests/day
- ✅ **Features**: Basic stock data, technical indicators

### Free Tier
- ⚡ **Rate Limit**: 60 requests/minute
- 📊 **Daily Limit**: 1,000 requests/day
- ✅ **Features**: All public features + fundamental data + market screener

### Basic Tier ($9/month)
- ⚡ **Rate Limit**: 120 requests/minute
- 📊 **Daily Limit**: 5,000 requests/day
- ✅ **Features**: All free features + portfolio analytics + intraday data

### Pro Tier ($29/month)
- ⚡ **Rate Limit**: 300 requests/minute
- 📊 **Daily Limit**: 20,000 requests/day
- ✅ **Features**: All basic features + WebSocket + priority support

### Enterprise Tier (Custom pricing)
- ⚡ **Rate Limit**: 1,000 requests/minute
- 📊 **Daily Limit**: 100,000 requests/day
- ✅ **Features**: All pro features + custom integration + dedicated support

---

## 🚀 Quick Start

### 1. Get Your API Key

#### Development Key (for testing)
```bash
# Default development key (already available)
export API_KEY="dev_key_12345"
```

#### Create New API Key (Admin)
```bash
curl -X POST "http://localhost:8000/api/admin/api-keys/create" \
  -H "X-API-Key: dev_key_12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My App",
    "tier": "free"
  }'
```

Response:
```json
{
  "success": true,
  "api_key": "vnsk_abc123xyz...",
  "tier": "free",
  "tier_config": {
    "name": "Free Tier",
    "max_requests_per_minute": 60,
    "max_requests_per_day": 1000
  },
  "message": "API key created successfully. Keep this key secret!",
  "usage": "Add header: X-API-Key: vnsk_abc123xyz..."
}
```

### 2. Use Your API Key

#### With curl
```bash
curl -H "X-API-Key: your_api_key_here" \
  "http://localhost:8000/api/stock/VNM"
```

#### With Python
```python
import requests

headers = {
    "X-API-Key": "your_api_key_here"
}

response = requests.get(
    "http://localhost:8000/api/stock/VNM",
    headers=headers
)

print(response.json())
```

#### With JavaScript/TypeScript
```typescript
const apiKey = "your_api_key_here";

const response = await fetch("http://localhost:8000/api/stock/VNM", {
  headers: {
    "X-API-Key": apiKey
  }
});

const data = await response.json();
```

#### With n8n
1. Add HTTP Request node
2. Add header: `X-API-Key` = `your_api_key_here`
3. Set URL: `http://vnstock-api:8000/api/stock/VNM`

---

## 📊 Check Your Rate Limit Status

```bash
curl -H "X-API-Key: your_api_key" \
  "http://localhost:8000/api/admin/rate-limit/status"
```

Response:
```json
{
  "success": true,
  "api_key": "vnsk_abc123xyz...",
  "tier": "free",
  "rate_limits": {
    "requests_per_minute": {
      "limit": 60,
      "remaining": 45,
      "used": 15
    },
    "requests_per_day": {
      "limit": 1000,
      "used": 127
    }
  },
  "usage": {
    "total_requests": 127,
    "last_used": "2025-11-10T10:30:00",
    "created_at": "2025-11-01T08:00:00"
  }
}
```

---

## ⚠️ Rate Limit Responses

### 429 Too Many Requests

When you exceed rate limit:

```json
{
  "detail": "Rate limit exceeded. Max 60 requests per minute."
}
```

Response headers:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 60
```

**What to do:**
1. Wait 60 seconds before retrying
2. Implement exponential backoff in your code
3. Consider upgrading to higher tier

---

## 🔒 Security Best Practices

### ✅ DO:
- Store API keys in environment variables
- Use different keys for dev/staging/production
- Rotate keys periodically
- Monitor usage for anomalies
- Use HTTPS in production

### ❌ DON'T:
- Commit API keys to Git
- Share keys between team members
- Expose keys in client-side code
- Use production keys for testing
- Ignore rate limit warnings

### Example: Secure Key Storage

#### `.env` file:
```bash
VNSTOCK_API_KEY=your_api_key_here
VNSTOCK_API_URL=https://api.vnstock.com
```

#### Python with python-dotenv:
```python
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("VNSTOCK_API_KEY")
API_URL = os.getenv("VNSTOCK_API_URL")
```

#### Node.js with dotenv:
```javascript
require('dotenv').config();

const API_KEY = process.env.VNSTOCK_API_KEY;
const API_URL = process.env.VNSTOCK_API_URL;
```

---

## 🛠️ Admin Endpoints

### List All API Keys
```bash
curl -H "X-API-Key: dev_key_12345" \
  "http://localhost:8000/api/admin/api-keys/list"
```

### Revoke API Key
```bash
curl -X POST "http://localhost:8000/api/admin/api-keys/revoke" \
  -H "X-API-Key: dev_key_12345" \
  -H "Content-Type: application/json" \
  -d '{"api_key": "key_to_revoke"}'
```

### View Tier Information
```bash
curl "http://localhost:8000/api/admin/api-keys/tiers"
```

### System Stats (Admin)
```bash
curl -H "X-API-Key: dev_key_12345" \
  "http://localhost:8000/api/admin/system/stats"
```

---

## 🔄 Upgrading Tiers

To upgrade your tier:

1. Contact support with your API key
2. Admin will update your key's tier
3. New limits take effect immediately

Or via API (Admin):
```bash
# Revoke old key
curl -X POST "http://localhost:8000/api/admin/api-keys/revoke" \
  -H "X-API-Key: admin_key" \
  -d '{"api_key": "old_key"}'

# Create new key with higher tier
curl -X POST "http://localhost:8000/api/admin/api-keys/create" \
  -H "X-API-Key: admin_key" \
  -d '{"name": "Upgraded Key", "tier": "pro"}'
```

---

## 💡 Tips & Tricks

### 1. Batch Requests
Instead of:
```python
# ❌ Bad: 100 requests
for symbol in ['VNM', 'VCB', 'HPG', ...]:  # 100 stocks
    data = get_stock_data(symbol)
```

Do this:
```python
# ✅ Good: 1 request
response = requests.post(
    "http://localhost:8000/api/screener/scan",
    json={"symbols": ['VNM', 'VCB', 'HPG', ...]},
    headers={"X-API-Key": api_key}
)
```

### 2. Cache Responses
```python
import time
from functools import lru_cache

@lru_cache(maxsize=100)
def get_stock_data_cached(symbol: str, timestamp: int):
    # timestamp updates every 5 minutes
    return get_stock_data(symbol)

# Use it
timestamp = int(time.time() / 300)  # 5 minute buckets
data = get_stock_data_cached("VNM", timestamp)
```

### 3. Exponential Backoff
```python
import time

def api_call_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers={"X-API-Key": api_key})

            if response.status_code == 429:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                print(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
                continue

            return response.json()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)

    raise Exception("Max retries exceeded")
```

### 4. Monitor Usage
```python
def get_with_monitoring(url):
    response = requests.get(url, headers={"X-API-Key": api_key})

    # Check rate limit headers
    limit = response.headers.get("X-RateLimit-Limit")
    remaining = response.headers.get("X-RateLimit-Remaining")

    if remaining and int(remaining) < 10:
        print(f"⚠️ Warning: Only {remaining} requests remaining!")

    return response.json()
```

---

## 📞 Support

- **Documentation**: http://localhost:8000/docs
- **GitHub Issues**: https://github.com/vnstock/vnstock-api/issues
- **Email**: support@vnstock.com (Enterprise only)

---

## 📝 Changelog

### v1.1.0 (2025-11-10)
- ✨ Added API key authentication
- ✨ Implemented rate limiting per tier
- ✨ Added admin endpoints for key management
- 🔒 Enhanced security with input validation

### v1.0.0 (2025-11-01)
- 🎉 Initial release
- ✅ Basic stock data endpoints
- ✅ Technical & fundamental indicators
- ✅ Market screener
