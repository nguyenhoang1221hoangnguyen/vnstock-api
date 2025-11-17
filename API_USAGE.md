# VNStock API - Hướng dẫn sử dụng

## Tóm tắt

VNStock API đã được sửa lỗi và đang hoạt động ổn định với vnstock v0.2.9.2.

**Status**: ✅ Hoạt động bình thường

## Các lỗi đã sửa

1. ✅ Lỗi vnai circular import
2. ✅ Lỗi terms & conditions vnstock
3. ✅ Cập nhật code tương thích vnstock 0.2.9.2
4. ✅ Thêm curl examples vào API documentation

## Endpoints API

### 1. Lấy toàn bộ dữ liệu cổ phiếu

**Endpoint:** `GET /api/stock/{symbol}`

**Curl examples:**
```bash
# Lấy dữ liệu VNM trong khoảng thời gian cụ thể
curl "http://localhost:8000/api/stock/VNM?start_date=2024-01-01&end_date=2024-01-31"

# Lấy dữ liệu VCB từ đầu năm đến hiện tại
curl "http://localhost:8000/api/stock/VCB?start_date=2024-01-01"

# Lấy dữ liệu HPG 5 năm gần nhất (không cần tham số)
curl "http://localhost:8000/api/stock/HPG"
```

**HTTP Request (n8n, Postman):**
```
GET http://localhost:8000/api/stock/VNM?start_date=2024-01-01&end_date=2024-01-31
```

**Response:** Bao gồm:
- Thông tin công ty
- Dữ liệu giá lịch sử
- Chỉ số kỹ thuật (SMA, EMA, MACD, RSI, BB, ATR, OBV, Ichimoku, PSAR, MFI, A/D, CMF, ADL)
- Chỉ số cơ bản (EPS, P/E, P/B, P/S, ROE, ROA, D/E, CR, NPM, RG, OCF, FCF)
- Chỉ số vĩ mô

---

### 2. Lấy dữ liệu giá

**Endpoint:** `GET /api/stock/{symbol}/price`

**Curl examples:**
```bash
curl "http://localhost:8000/api/stock/VNM/price?start_date=2024-01-01&end_date=2024-01-31"
curl "http://localhost:8000/api/stock/VCB/price"
```

**HTTP Request:**
```
GET http://localhost:8000/api/stock/VNM/price?start_date=2024-01-01&end_date=2024-01-31
```

---

### 3. Lấy chỉ số kỹ thuật

**Endpoint:** `GET /api/stock/{symbol}/technical`

**Curl examples:**
```bash
curl "http://localhost:8000/api/stock/VNM/technical?start_date=2024-01-01&end_date=2024-01-31"
curl "http://localhost:8000/api/stock/HPG/technical"
```

**HTTP Request:**
```
GET http://localhost:8000/api/stock/VNM/technical?start_date=2024-01-01&end_date=2024-01-31
```

---

### 4. Lấy chỉ số cơ bản

**Endpoint:** `GET /api/stock/{symbol}/fundamental`

**Curl examples:**
```bash
curl "http://localhost:8000/api/stock/VNM/fundamental"
curl "http://localhost:8000/api/stock/VCB/fundamental"
```

**HTTP Request:**
```
GET http://localhost:8000/api/stock/VNM/fundamental
```

---

### 5. Lấy thông tin công ty

**Endpoint:** `GET /api/stock/{symbol}/company`

**Curl examples:**
```bash
curl "http://localhost:8000/api/stock/VNM/company"
curl "http://localhost:8000/api/stock/HPG/company"
```

**HTTP Request:**
```
GET http://localhost:8000/api/stock/VNM/company
```

---

### 6. Health check

**Endpoint:** `GET /health`

**Curl:**
```bash
curl "http://localhost:8000/health"
```

**Response:**
```json
{
  "status": "healthy",
  "service": "vnstock-api"
}
```

---

## Sử dụng với n8n

1. Thêm HTTP Request node
2. Method: GET
3. URL: `http://vnstock-api:8000/api/stock/VNM?start_date=2024-01-01&end_date=2024-01-31`
4. Headers: `Content-Type: application/json`

## Sử dụng với Postman

1. Tạo request mới
2. Method: GET
3. URL: `http://localhost:8000/api/stock/VNM?start_date=2024-01-01&end_date=2024-01-31`
4. Send

## API Documentation

Truy cập Swagger UI tại: **http://localhost:8000/docs**

Tại đây bạn có thể:
- Xem tất cả endpoints
- Thử nghiệm API trực tiếp
- Xem curl examples
- Copy HTTP request để import vào các tools

## Docker Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Rebuild
docker-compose up -d --build

# View logs
docker logs vnstock-api
docker logs n8n

# Check status
docker ps
```

## Services

- **VNStock API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **n8n**: http://localhost:5678 (admin/admin123)

## Version Info

- **n8n**: 1.118.2 (Latest - November 3, 2025)
- **vnstock**: 0.2.9.2
- **FastAPI**: 0.109.0
- **Python**: 3.11

## n8n Features (v1.118.2)

Phiên bản mới nhất với các tính năng:
- ✨ AI Workflow Builder - Tạo workflows từ prompts
- 🤖 AI Agent v3 với improved tool execution
- 💬 Respond to Chat node với Human-in-the-Loop
- 🔄 Upgraded AI và HTTP Request nodes
- 🐍 Code node hỗ trợ Python phiên bản mới
- 🔧 Database migration tools (SQLite ↔ Postgres)
