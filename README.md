# VNStock API - Vietnam Stock Market Data API

API để lấy dữ liệu chứng khoán thị trường Việt Nam và tính toán các chỉ số phân tích kỹ thuật và cơ bản.

## Tính năng

### 📊 Dữ liệu Giá
- Lấy dữ liệu giá lịch sử từ ngày niêm yết hoặc trong khoảng thời gian tùy chọn
- Bao gồm: Open, High, Low, Close, Volume

### 🏢 Thông tin Công ty
- Tên công ty, mã chứng khoán
- Ngành, lĩnh vực kinh doanh
- Vốn hóa thị trường
- Số cổ phiếu đang lưu hành
- Website, mô tả doanh nghiệp

### 📈 Chỉ số Kỹ thuật (Technical Indicators)
- **SMA** - Simple Moving Average (20, 50, 100, 200)
- **EMA** - Exponential Moving Average (12, 26, 50, 200)
- **MACD** - Moving Average Convergence Divergence
- **RSI** - Relative Strength Index
- **BB** - Bollinger Bands
- **ATR** - Average True Range
- **OBV** - On Balance Volume
- **Ichimoku** - Ichimoku Cloud
- **PSAR** - Parabolic SAR
- **MFI** - Money Flow Index
- **A/D** - Accumulation/Distribution
- **CMF** - Chaikin Money Flow
- **ADL** - Advance/Decline Line

### 💰 Chỉ số Cơ bản (Fundamental Indicators)
- **EPS** - Earnings Per Share
- **P/E** - Price to Earnings Ratio
- **P/B** - Price to Book Ratio
- **P/S** - Price to Sales Ratio
- **P/CF** - Price to Cash Flow Ratio
- **DY** - Dividend Yield
- **EV/EBITDA** - Enterprise Value to EBITDA
- **PEG** - Price/Earnings to Growth Ratio
- **ROE** - Return on Equity
- **ROA** - Return on Assets
- **D/E** - Debt to Equity Ratio
- **CR** - Current Ratio
- **NPM** - Net Profit Margin
- **RG** - Revenue Growth
- **OCF** - Operating Cash Flow
- **FCF** - Free Cash Flow

### 🌍 Chỉ số Kinh tế Vĩ mô (Macro Indicators)
- **GDP** - Gross Domestic Product
- **CPI** - Consumer Price Index
- **IR** - Interest Rate
- **EXR** - Exchange Rate
- **UR** - Unemployment Rate
- **FGI** - Fear and Greed Index
- **PCR** - Put/Call Ratio

## Cài đặt

### Yêu cầu
- Docker & Docker Compose (khuyến nghị)
- HOẶC Python 3.8+ & pip (cho development)

## 🐳 Chạy với Docker (Khuyến nghị)

### Quick Start

```bash
cd vnstock-api
./docker-start.sh
```

Chỉ cần một lệnh, hệ thống sẽ tự động:
- Build Docker images
- Khởi động VNStock API
- Khởi động n8n
- Kết nối tất cả services

### Truy cập Services

- **VNStock API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **n8n**: http://localhost:5678
  - Username: `admin`
  - Password: `admin123`

### Các lệnh Docker hữu ích

```bash
# Khởi động services
./docker-start.sh

# Dừng services
./docker-stop.sh

# Rebuild images (sau khi thay đổi code)
./docker-rebuild.sh

# Xem logs
docker-compose logs -f
docker-compose logs -f vnstock-api
docker-compose logs -f n8n

# Kiểm tra trạng thái
docker-compose ps

# Dừng và xóa volumes
docker-compose down -v
```

### Kết nối từ n8n đến VNStock API

Trong n8n, sử dụng hostname `vnstock-api` thay vì `localhost`:

```
URL: http://vnstock-api:8000/api/stock/VNM
```

## 💻 Chạy Local (Development)

### Các bước cài đặt

1. Clone repository:
```bash
cd vnstock-api
```

2. Tạo virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Trên Linux/Mac
# hoặc
venv\Scripts\activate  # Trên Windows
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

### Chạy API Server

```bash
# Cách 1: Sử dụng script
./run.sh

# Cách 2: Sử dụng uvicorn trực tiếp
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Cách 3: Chạy từ main.py
python -m app.main
```

Server sẽ chạy tại: `http://localhost:8000`

API Documentation (Swagger UI): `http://localhost:8000/docs`

### API Endpoints

#### 1. Lấy toàn bộ dữ liệu cổ phiếu
```http
GET /api/stock/{symbol}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

**Ví dụ:**
```bash
curl "http://localhost:8000/api/stock/VNM?start_date=2024-01-01&end_date=2024-12-31"
```

**Response:**
```json
{
  "symbol": "VNM",
  "company_info": {
    "company_name": "Vinamilk",
    "exchange": "HOSE",
    "industry": "Food & Beverage",
    ...
  },
  "price_data": [...],
  "technical_indicators": {
    "SMA": {...},
    "EMA": {...},
    "MACD": {...},
    "RSI": {...},
    ...
  },
  "fundamental_indicators": {
    "EPS": 5000,
    "PE": 15.2,
    "ROE": 25.5,
    ...
  },
  "macro_indicators": {...},
  "metadata": {
    "total_records": 250,
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "current_price": 75500
  }
}
```

#### 2. Lấy chỉ dữ liệu giá
```http
GET /api/stock/{symbol}/price?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

#### 3. Lấy chỉ số kỹ thuật
```http
GET /api/stock/{symbol}/technical?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
```

#### 4. Lấy chỉ số cơ bản
```http
GET /api/stock/{symbol}/fundamental
```

#### 5. Lấy thông tin công ty
```http
GET /api/stock/{symbol}/company
```

#### 6. Health Check
```http
GET /health
```

## 🔗 Tích hợp với n8n

API này được thiết kế để tích hợp dễ dàng với n8n:

### Cách 1: Sử dụng Docker Stack (Khuyến nghị)

Khi chạy bằng `./docker-start.sh`, cả VNStock API và n8n đều ở trong cùng một network Docker.

**Trong n8n HTTP Request Node:**

1. Truy cập n8n tại: http://localhost:5678
2. Login với username: `admin`, password: `admin123`
3. Tạo workflow mới
4. Thêm **HTTP Request Node**
5. Cấu hình:
   - Method: `GET`
   - URL: `http://vnstock-api:8000/api/stock/VNM`
   - Query Parameters (optional):
     - `start_date`: YYYY-MM-DD
     - `end_date`: YYYY-MM-DD

**Lưu ý**: Sử dụng hostname `vnstock-api` (tên service trong docker-compose) thay vì `localhost`.

### Cách 2: n8n riêng biệt

Nếu bạn đã có n8n chạy riêng, sử dụng:
- URL: `http://localhost:8000/api/stock/VNM` (nếu trên cùng máy)
- URL: `http://your-server-ip:8000/api/stock/VNM` (nếu khác máy)

### Ví dụ Workflow n8n

```json
{
  "nodes": [
    {
      "parameters": {
        "method": "GET",
        "url": "http://vnstock-api:8000/api/stock/VNM",
        "options": {
          "queryParameters": {
            "parameters": [
              {
                "name": "start_date",
                "value": "2024-01-01"
              },
              {
                "name": "end_date",
                "value": "2024-12-31"
              }
            ]
          }
        }
      },
      "name": "Get VNM Stock Data",
      "type": "n8n-nodes-base.httpRequest"
    }
  ]
}
```

Dữ liệu JSON trả về có thể được xử lý trực tiếp bởi AI agents hoặc các nodes khác trong n8n.

### Ví dụ với Python

```python
import requests

# Lấy toàn bộ dữ liệu
response = requests.get(
    "http://localhost:8000/api/stock/VNM",
    params={
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
)

data = response.json()
print(f"Công ty: {data['company_info']['company_name']}")
print(f"Giá hiện tại: {data['metadata']['current_price']}")
print(f"P/E: {data['fundamental_indicators']['PE']}")
print(f"RSI: {data['technical_indicators']['RSI']}")
```

### Ví dụ với cURL

```bash
# Lấy dữ liệu VNM từ ngày niêm yết
curl "http://localhost:8000/api/stock/VNM"

# Lấy dữ liệu VCB trong khoảng thời gian
curl "http://localhost:8000/api/stock/VCB?start_date=2024-01-01&end_date=2024-12-31"

# Lấy chỉ thông tin công ty
curl "http://localhost:8000/api/stock/HPG/company"

# Lấy chỉ số kỹ thuật
curl "http://localhost:8000/api/stock/FPT/technical"
```

## 📁 Cấu trúc Dự án

```
vnstock-api/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py                # API endpoints
│   ├── core/
│   │   └── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py               # Pydantic models
│   ├── services/
│   │   ├── __init__.py
│   │   └── vnstock_service.py       # VNStock integration
│   └── utils/
│       ├── __init__.py
│       ├── technical_indicators.py  # Technical analysis
│       └── fundamental_indicators.py # Fundamental analysis
├── Dockerfile                        # Docker image configuration
├── docker-compose.yml                # Docker stack với n8n
├── .dockerignore                     # Docker ignore file
├── .env                              # Environment variables
├── .env.example                      # Environment template
├── docker-start.sh                   # Start Docker stack
├── docker-stop.sh                    # Stop Docker stack
├── docker-rebuild.sh                 # Rebuild Docker images
├── run.sh                            # Run local server
├── example_usage.py                  # Usage examples
├── requirements.txt                  # Python dependencies
├── README.md                         # Documentation
└── .gitignore                        # Git ignore file
```

## ⚠️ Lưu ý

- Dữ liệu được lấy từ thư viện `vnstock3`
- Một số chỉ số vĩ mô có thể chưa khả dụng do giới hạn của nguồn dữ liệu
- API sử dụng CORS mở (`allow_origins=["*"]`) - nên giới hạn trong môi trường production
- Thời gian xử lý phụ thuộc vào khoảng thời gian dữ liệu được yêu cầu
- Trong Docker: VNStock API và n8n kết nối qua Docker network `vnstock-network`
- Dữ liệu n8n được lưu trong Docker volume `n8n_data` - không bị mất khi restart containers

## 🔧 Cấu hình

### Environment Variables (.env)

```bash
# n8n Configuration
N8N_BASIC_AUTH_USER=admin          # n8n username
N8N_BASIC_AUTH_PASSWORD=admin123   # n8n password
N8N_HOST=localhost
WEBHOOK_URL=http://localhost:5678/

# Timezone
TIMEZONE=Asia/Ho_Chi_Minh

# VNStock API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

### Ports

- **8000**: VNStock API
- **5678**: n8n Web UI

### Docker Networks

- **vnstock-network**: Bridge network kết nối VNStock API và n8n

### Docker Volumes

- **n8n_data**: Lưu trữ workflows và dữ liệu n8n
- **./logs**: Logs của VNStock API (mount từ host)
- **./n8n/workflows**: Workflows của n8n (mount từ host)

## Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng tạo issue hoặc pull request.

## License

MIT License

## Liên hệ

- GitHub: [vnstock](https://github.com/thinh-vu/vnstock)
- Documentation: http://localhost:8000/docs

## 🎯 Version Info

- **n8n**: 1.118.2 (Latest - November 3, 2025)
  - ✨ AI Workflow Builder - Tạo workflows từ prompts
  - 🤖 AI Agent v3 với improved tool execution
  - 💬 Respond to Chat node với Human-in-the-Loop
  - 🔄 Upgraded AI và HTTP Request nodes
  - 🐍 Code node hỗ trợ Python phiên bản mới
  - 🔧 Database migration tools (SQLite ↔ Postgres)
- **vnstock**: 0.2.9.2 (Stable)
- **FastAPI**: 0.109.0
- **Python**: 3.11

## 📊 Changelog

### Version 1.0.1 (November 2025)
- ✅ Cập nhật n8n lên 1.118.2 (Latest)
- ✅ Thêm curl examples vào tất cả API endpoints
- ✅ Thêm HTTP Request templates cho n8n/Postman
- ✅ Sửa lỗi vnai circular import
- ✅ Downgrade vnstock về 0.2.9.2 để tránh lỗi
- ✅ Cải thiện API documentation
- ✅ Thêm API_USAGE.md với hướng dẫn chi tiết

### Version 1.0.0 (2024)
- ✅ Phát hành phiên bản đầu tiên
- ✅ Hỗ trợ đầy đủ 13 chỉ số kỹ thuật
- ✅ Hỗ trợ 16 chỉ số cơ bản
- ✅ Tích hợp với vnstock
- ✅ API documentation với Swagger UI
- ✅ Docker support với docker-compose
- ✅ Tích hợp sẵn n8n trong Docker stack
- ✅ Auto health check
- ✅ Production-ready với non-root user

## 🚀 Roadmap

- [ ] Thêm authentication/API keys
- [ ] Rate limiting
- [ ] Caching layer (Redis)
- [ ] WebSocket support cho real-time data
- [ ] Thêm các chỉ số vĩ mô từ nguồn khác
- [ ] Export dữ liệu sang Excel/CSV
- [ ] Kubernetes deployment templates
- [ ] Monitoring với Prometheus/Grafana
