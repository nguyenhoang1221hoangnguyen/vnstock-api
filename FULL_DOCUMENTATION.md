# VNStock API - Tài Liệu Toàn Diện (Full Documentation)

**Phiên bản**: 1.0.1
**Ngày cập nhật**: November 2025
**Tác giả**: VNStock Team

---

## Mục Lục

1. [Tổng Quan Hệ Thống](#1-tổng-quan-hệ-thống)
2. [Kiến Trúc Hệ Thống](#2-kiến-trúc-hệ-thống)
3. [Backend API](#3-backend-api)
4. [Frontend Application](#4-frontend-application)
5. [Database Schema](#5-database-schema)
6. [Services và Business Logic](#6-services-và-business-logic)
7. [Deployment và Infrastructure](#7-deployment-và-infrastructure)
8. [API Reference](#8-api-reference)
9. [Development Guide](#9-development-guide)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Tổng Quan Hệ Thống

### 1.1 Giới Thiệu

VNStock API là hệ thống phân tích chứng khoán thị trường Việt Nam được xây dựng với:
- **Backend**: FastAPI (Python) - RESTful API server
- **Frontend**: React + TypeScript - Modern SPA (Single Page Application)
- **Database**: SQLite với SQLAlchemy ORM
- **Automation**: n8n workflow automation (optional)
- **Containerization**: Docker & Docker Compose

### 1.2 Tính Năng Chính

#### A. Dữ Liệu Thị Trường
- ✅ Dữ liệu giá lịch sử (OHLCV)
- ✅ Dữ liệu intraday với nhiều timeframes (1m, 5m, 15m, 30m, 1h, 3h, 6h, 1d)
- ✅ Thông tin công ty chi tiết
- ✅ Báo cáo tài chính (Balance Sheet, Income Statement, Cash Flow)

#### B. Phân Tích Kỹ Thuật (Technical Analysis)
- 13 chỉ số kỹ thuật: SMA, EMA, MACD, RSI, Bollinger Bands, ATR, OBV, Ichimoku, PSAR, MFI, A/D, CMF, ADL
- 12 mô hình nến Nhật (Candlestick Patterns): Doji, Hammer, Engulfing, Morning Star, v.v.

#### C. Phân Tích Cơ Bản (Fundamental Analysis)
- 16 chỉ số tài chính: EPS, P/E, P/B, ROE, ROA, D/E, CR, NPM, RG, OCF, FCF, v.v.

#### D. Market Tools
- **Market Screener**: Quét cổ phiếu theo tiêu chí tùy chỉnh
- **Market Heatmap**: Hiển thị toàn cảnh thị trường theo sectors
- **Portfolio Analytics**: Phân tích danh mục đầu tư
- **News Aggregator**: Tổng hợp tin tức thị trường

#### E. Tính Năng Nâng Cao
- In-memory caching với TTL
- Rate limiting và API key authentication
- Background scheduler cho data updates
- Real-time auto-refresh (frontend)
- Responsive web interface

### 1.3 Tech Stack

```
Backend:
├── FastAPI 0.109.0          # Web framework
├── vnstock 0.2.9.2          # Vietnam stock data library
├── pandas 2.1.4             # Data manipulation
├── ta 0.11.0                # Technical analysis
├── SQLAlchemy 2.0.25        # ORM
├── APScheduler 3.10.4       # Background jobs
└── Uvicorn 0.27.0           # ASGI server

Frontend:
├── React 19.2.0             # UI framework
├── TypeScript 4.9.5         # Type safety
├── Axios 1.13.2             # HTTP client
├── lightweight-charts 3.8.0 # Charting library
├── Recharts 3.3.0           # Additional charts
└── Lucide React 0.553.0     # Icons

Infrastructure:
├── Docker                   # Containerization
├── Docker Compose           # Multi-container orchestration
├── n8n 1.118.2              # Workflow automation (optional)
└── Nginx (production)       # Reverse proxy
```

---

## 2. Kiến Trúc Hệ Thống

### 2.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Client Layer                            │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │   Browser    │  │   n8n Web    │  │  External API        │  │
│  │  (React SPA) │  │   Interface  │  │  Clients (curl/etc)  │  │
│  └──────┬───────┘  └──────┬───────┘  └──────────┬───────────┘  │
│         │                 │                      │              │
└─────────┼─────────────────┼──────────────────────┼──────────────┘
          │                 │                      │
          ▼                 ▼                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                          │
├─────────────────────────────────────────────────────────────────┤
│                    FastAPI Application                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  CORS Middleware │ Auth Middleware │ Rate Limiter        │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                       │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌────────────────────────┐ │
│  │   Routes    │  │  Services   │  │   Utilities            │ │
│  │             │  │             │  │                        │ │
│  │ • Stock     │  │ • VNStock   │  │ • Technical Analyzer   │ │
│  │ • Screener  │  │ • Intraday  │  │ • Fundamental Analyzer │ │
│  │ • Heatmap   │  │ • Market    │  │ • Pattern Detector     │ │
│  │ • Portfolio │  │ • News      │  │ • Validators           │ │
│  │ • News      │  │ • Stock     │  │                        │ │
│  │ • Admin     │  │   Data      │  │                        │ │
│  └─────────────┘  └─────────────┘  └────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                       Data Access Layer                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────┐│
│  │   Cache      │  │   Database   │  │  External APIs        ││
│  │  (In-Memory) │  │   (SQLite)   │  │  (vnstock/VCI/TCBS)   ││
│  └──────────────┘  └──────────────┘  └───────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Background Jobs Layer                      │
├─────────────────────────────────────────────────────────────────┤
│  APScheduler - Stock Data Updater - Cache Cleanup              │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Interaction Flow

```
User Request Flow:
1. User → React App → API Service (axios)
2. API Service → FastAPI Endpoint
3. FastAPI → Check Cache
4. If Cache Miss → Service Layer → vnstock Library
5. Process Data → Calculate Indicators
6. Store in Cache + Database
7. Return JSON Response
8. React App Updates UI
```

### 2.3 Directory Structure

```
vnstock-api/
├── app/                                 # Backend application
│   ├── __init__.py
│   ├── main.py                         # FastAPI app entry point
│   │
│   ├── api/                            # API routes
│   │   ├── __init__.py
│   │   ├── routes.py                   # Main API endpoints
│   │   └── admin_routes.py             # Admin endpoints
│   │
│   ├── core/                           # Core functionality
│   │   ├── __init__.py
│   │   ├── auth.py                     # API key authentication & rate limiting
│   │   ├── cache.py                    # In-memory caching
│   │   ├── validators.py               # Input validators
│   │   └── vnstock_patch.py            # vnstock library patches
│   │
│   ├── models/                         # Data models
│   │   ├── __init__.py
│   │   └── schemas.py                  # Pydantic schemas
│   │
│   ├── database/                       # Database layer
│   │   ├── __init__.py
│   │   ├── database.py                 # DB connection & session
│   │   └── models.py                   # SQLAlchemy models
│   │
│   ├── services/                       # Business logic services
│   │   ├── __init__.py
│   │   ├── vnstock_service.py          # VNStock API integration
│   │   ├── intraday_service.py         # Intraday data processing
│   │   ├── stock_data_service.py       # Stock data CRUD
│   │   ├── market_screener.py          # Stock screener
│   │   ├── market_heatmap.py           # Market heatmap
│   │   ├── portfolio_analytics.py      # Portfolio analysis
│   │   └── news_aggregator.py          # News aggregation
│   │
│   ├── scheduler/                      # Background jobs
│   │   ├── __init__.py
│   │   └── stock_updater.py            # Scheduled data updates
│   │
│   └── utils/                          # Utility modules
│       ├── __init__.py
│       ├── technical_indicators.py     # Technical analysis
│       ├── fundamental_indicators.py   # Fundamental analysis
│       └── candlestick_patterns.py     # Pattern detection
│
├── frontend/                           # Frontend application
│   ├── public/
│   │   ├── index.html
│   │   └── manifest.json
│   │
│   ├── src/
│   │   ├── App.tsx                     # Main app component
│   │   ├── App.css                     # Global styles
│   │   ├── index.tsx                   # Entry point
│   │   │
│   │   ├── components/                 # React components
│   │   │   ├── TradingViewChart.tsx    # Chart component
│   │   │   ├── IndicatorsPanel.tsx     # Indicators display
│   │   │   ├── Watchlist.tsx           # Stock watchlist
│   │   │   ├── MarketScreener.tsx      # Screener UI
│   │   │   ├── NewsFeed.tsx            # News feed
│   │   │   ├── StockChart.tsx          # Alternative chart
│   │   │   └── CandlestickPatterns.tsx # Pattern display
│   │   │
│   │   ├── services/                   # Frontend services
│   │   │   ├── api.ts                  # API client
│   │   │   └── cache.ts                # Client-side cache
│   │   │
│   │   └── types/                      # TypeScript types
│   │       └── stock.ts                # Stock data types
│   │
│   ├── package.json                    # NPM dependencies
│   └── tsconfig.json                   # TypeScript config
│
├── logs/                               # Application logs
├── n8n/                                # n8n workflows
├── .env                                # Environment variables
├── .env.example                        # Environment template
├── Dockerfile                          # Docker image definition
├── docker-compose.yml                  # Multi-container setup
├── requirements.txt                    # Python dependencies
├── run.sh                              # Local dev server script
├── docker-start.sh                     # Docker startup script
├── docker-stop.sh                      # Docker stop script
├── docker-rebuild.sh                   # Docker rebuild script
│
└── Documentation/
    ├── README.md                       # Quick start guide
    ├── API_USAGE.md                    # API usage examples
    ├── AUTHENTICATION.md               # Auth documentation
    ├── DOCKER_GUIDE.md                 # Docker guide
    ├── DEPLOYMENT_SUMMARY.md           # Deployment guide
    ├── IMPROVEMENTS_ROADMAP.md         # Future improvements
    ├── SUMMARY.md                      # Project summary
    └── FULL_DOCUMENTATION.md           # This file
```

---

## 3. Backend API

### 3.1 FastAPI Application (app/main.py)

#### Initialization Flow

```python
# 1. Patch vnstock library
from .core import vnstock_patch

# 2. Create FastAPI app
app = FastAPI(
    title="VNStock API",
    version="1.0.0",
    description="Vietnam Stock Market Data API"
)

# 3. Configure CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"])

# 4. Include routers
app.include_router(router)
app.include_router(admin_router)

# 5. Startup event
@app.on_event("startup")
async def startup_event():
    init_db()          # Initialize database
    init_scheduler()   # Start background jobs

# 6. Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    stop_scheduler()   # Stop background jobs
    close_db()         # Close database connections
```

### 3.2 API Routes Architecture

#### Main Routes (app/api/routes.py)

**Endpoint Categories:**

1. **Stock Data Endpoints**
   - `GET /api/stock/{symbol}` - Complete stock data
   - `GET /api/stock/{symbol}/price` - Price data only
   - `GET /api/stock/{symbol}/technical` - Technical indicators
   - `GET /api/stock/{symbol}/fundamental` - Fundamental indicators
   - `GET /api/stock/{symbol}/company` - Company info
   - `GET /api/stock/{symbol}/intraday` - Intraday candles
   - `GET /api/stock/{symbol}/intervals` - Supported intervals
   - `GET /api/stock/{symbol}/candlestick-patterns` - Pattern detection

2. **Market Screener Endpoints**
   - `POST /api/screener/scan` - Custom scan
   - `GET /api/screener/presets` - List presets
   - `GET /api/screener/preset/{name}` - Preset scan

3. **Market Heatmap Endpoints**
   - `GET /api/heatmap/market` - Market overview
   - `GET /api/heatmap/sector/{sector}` - Sector heatmap

4. **Portfolio Analytics Endpoints**
   - `POST /api/portfolio/analyze` - Analyze portfolio
   - `GET /api/portfolio/compare-market` - Compare with market

5. **News Aggregator Endpoints**
   - `GET /api/news/latest` - Latest news
   - `GET /api/news/sentiment` - Market sentiment
   - `GET /api/news/search` - Search news

6. **Cache Management Endpoints**
   - `GET /api/cache/stats` - Cache statistics
   - `POST /api/cache/clear` - Clear cache
   - `POST /api/cache/cleanup` - Cleanup expired

7. **Database & Scheduler Endpoints**
   - `GET /api/admin/scheduler/status` - Scheduler status
   - `POST /api/admin/database/populate` - Initial populate
   - `POST /api/admin/database/update-stale` - Update stale data
   - `GET /api/admin/database/stats` - Database stats

#### Admin Routes (app/api/admin_routes.py)

**Authentication & Rate Limiting:**

```python
# API Key Tiers
API_TIERS = {
    'free': {
        'max_requests_per_minute': 60,
        'max_requests_per_day': 1000
    },
    'basic': {
        'max_requests_per_minute': 120,
        'max_requests_per_day': 5000
    },
    'pro': {
        'max_requests_per_minute': 300,
        'max_requests_per_day': 20000
    },
    'enterprise': {
        'max_requests_per_minute': 1000,
        'max_requests_per_day': 100000
    }
}
```

**Admin Endpoints:**
- `POST /api/admin/api-keys/create` - Create API key
- `GET /api/admin/api-keys/list` - List all keys
- `POST /api/admin/api-keys/revoke` - Revoke key
- `GET /api/admin/api-keys/tiers` - Tier information
- `GET /api/admin/rate-limit/status` - Rate limit status
- `GET /api/admin/system/health` - System health
- `GET /api/admin/system/stats` - System statistics

### 3.3 Core Modules

#### A. Authentication (app/core/auth.py)

**Features:**
- API Key generation & validation
- Rate limiting (per minute & per day)
- Multiple tier support
- Thread-safe request tracking

**Usage:**
```python
# Require API key
@router.get("/protected")
async def protected_route(api_key: str = Depends(require_api_key)):
    return {"message": "Authorized"}

# Create new API key
api_key = APIKeyManager.create_api_key(
    name="My App",
    tier="pro",
    max_requests_per_minute=300,
    max_requests_per_day=20000
)
```

#### B. Caching (app/core/cache.py)

**InMemoryCache Class:**

```python
class InMemoryCache:
    def __init__(self, default_ttl: int = 300):  # 5 minutes
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = Lock()  # Thread-safe

    def get(self, key: str) -> Optional[Any]
    def set(self, key: str, value: Any, ttl: Optional[int] = None)
    def delete(self, key: str) -> bool
    def clear(self)
    def cleanup_expired(self) -> int
    def get_stats(self) -> Dict[str, Any]

    # Decorator for caching function results
    @cache.cache_result(ttl=300)
    def expensive_function(param):
        return result
```

**Cache Usage:**
- Stock data: 2 minutes TTL
- Intraday data: 60 seconds TTL
- Patterns: 5 minutes TTL
- News: 1 minute TTL

#### C. Validators (app/core/validators.py)

Input validation for:
- Stock symbols (uppercase, 3-5 chars)
- Date formats (YYYY-MM-DD)
- Numeric ranges
- Exchange codes (HOSE, HNX, UPCOM)

---

## 4. Frontend Application

### 4.1 React Architecture

#### Main App Component (src/App.tsx)

**State Management:**
```typescript
interface AppState {
    activeTab: 'trading' | 'screener' | 'news';
    selectedSymbol: string;
    stockData: StockData | null;
    loading: boolean;
    error: string | null;
    dateRange: { start: string; end: string };
    autoRefresh: boolean;
    currentInterval: string;  // '1m', '5m', '15m', '30m', '1h', '3h', '6h', '1d'
}
```

**Key Features:**
1. **Tab Navigation**: Trading, Screener, News
2. **Date Range Picker**: With quick select buttons
3. **Auto-refresh**: 60-second intervals
4. **Interval Switcher**: Support for multiple timeframes
5. **Real-time Updates**: WebSocket support (planned)

### 4.2 Components

#### A. TradingViewChart.tsx
- Lightweight Charts integration
- Candlestick rendering
- Volume bars
- Tooltip with OHLCV data
- Interval switcher
- Responsive design

#### B. IndicatorsPanel.tsx
- Display fundamental indicators
- Color-coded metrics
- Grid layout
- Real-time updates

#### C. Watchlist.tsx
- Popular stocks list (VNM, VCB, HPG, etc.)
- Click to load
- Highlight active symbol

#### D. MarketScreener.tsx
- Custom filters
- Preset screeners
- Results table
- Export functionality

#### E. NewsFeed.tsx
- Latest market news
- Sentiment analysis
- Source filtering
- Search functionality

#### F. CandlestickPatterns.tsx
- Pattern detection results
- Visual indicators
- Pattern descriptions
- Latest N patterns view

### 4.3 Services

#### API Service (src/services/api.ts)

```typescript
export const apiService = {
    // Stock data
    getStockData(symbol, startDate?, endDate?): Promise<StockData>
    getLatestPrice(symbol): Promise<StockData>
    getIntradayData(symbol, interval, start?, end?): Promise<any>

    // Market tools
    screenStocks(filters, exchange, limit): Promise<any>
    getMarketHeatmap(exchange): Promise<any>
    analyzePortfolio(holdings, periodDays): Promise<any>

    // News
    getLatestNews(symbol?, limit, sources?): Promise<any>
    getMarketSentiment(days): Promise<any>

    // Patterns
    getCandlestickPatterns(symbol, start?, end?, latestN?): Promise<any>

    // Cache
    getCacheStats(): Promise<any>
    clearCache(): Promise<any>
}
```

#### Cache Service (src/services/cache.ts)

Client-side caching with TTL:
```typescript
class CacheService {
    async cached<T>(
        key: string,
        fetcher: () => Promise<T>,
        ttl: number
    ): Promise<T>
}
```

### 4.4 Types (src/types/stock.ts)

```typescript
interface StockData {
    symbol: string;
    company_info: CompanyInfo;
    price_data: PriceData[];
    technical_indicators?: TechnicalIndicators;
    fundamental_indicators?: FundamentalIndicators;
    macro_indicators?: MacroIndicators;
    metadata: Metadata;
}

interface PriceData {
    time: string;
    open: number;
    high: number;
    low: number;
    close: number;
    volume: number;
}
```

---

## 5. Database Schema

### 5.1 SQLAlchemy Models

#### StockScreeningData Model

```python
class StockScreeningData(Base):
    __tablename__ = "stock_screening_data"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    exchange = Column(String(10), index=True)

    # Company Info
    company_name = Column(String(255))
    industry = Column(String(100))
    sector = Column(String(100))

    # Price Data
    current_price = Column(Float)
    price_change_30d = Column(Float)  # % change
    volume = Column(Float)

    # Financial Ratios
    pe = Column(Float)   # P/E ratio
    pb = Column(Float)   # P/B ratio
    roe = Column(Float)  # Return on Equity
    eps = Column(Float)  # Earnings per Share
    market_cap = Column(Float)

    # Technical Indicators
    rsi = Column(Float)  # RSI 14

    # Metadata
    score = Column(Float, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Indexes
    __table_args__ = (
        Index('idx_exchange_score', 'exchange', 'score'),
        Index('idx_pe_roe', 'pe', 'roe'),
        Index('idx_last_updated', 'last_updated'),
    )
```

#### ScreeningJobLog Model

```python
class ScreeningJobLog(Base):
    __tablename__ = "screening_job_log"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String(50))  # 'full_scan', 'update_scan', 'daily_update'
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    status = Column(String(20))  # 'running', 'completed', 'failed'
    stocks_processed = Column(Integer, default=0)
    stocks_updated = Column(Integer, default=0)
    stocks_failed = Column(Integer, default=0)
    error_message = Column(String(500))

    __table_args__ = (
        Index('idx_job_type_status', 'job_type', 'status'),
        Index('idx_started_at', 'started_at'),
    )
```

### 5.2 Database Operations

#### Initialization (app/database/database.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./vnstock.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)

def get_db_session():
    """Get database session (context manager)"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 6. Services và Business Logic

### 6.1 VNStock Service (app/services/vnstock_service.py)

**Primary service for interacting with vnstock library v0.2.9.2**

```python
class VNStockService:
    def __init__(self):
        self.stock = None
        self._Vnstock = None
        self.cache = get_cache()

    # Main Methods
    def get_listing_date(symbol: str) -> Optional[str]
    def get_company_info(symbol: str) -> Dict[str, Any]
    def get_price_data(symbol, start_date?, end_date?) -> pd.DataFrame
    def get_financial_statements(symbol, period, lang) -> Dict[str, pd.DataFrame]
    def get_macro_data() -> Dict[str, Any]
    def get_complete_stock_data(symbol, start_date?, end_date?) -> Dict[str, Any]
```

**Data Flow:**
1. Initialize vnstock library (lazy loading)
2. Fetch data from VCI/TCBS sources
3. Process and transform data
4. Calculate indicators
5. Cache results
6. Return structured JSON

### 6.2 Intraday Service (app/services/intraday_service.py)

**Converts tick data to candlesticks**

```python
class IntradayService:
    INTERVAL_MINUTES = {
        '1m': 1, '5m': 5, '15m': 15, '30m': 30,
        '1h': 60, '3h': 180, '6h': 360, '1d': 1440
    }

    def get_intraday_candles(
        symbol, interval='5m', start_date?, end_date?, limit=5000
    ) -> List[Dict]

    def _aggregate_ticks_to_candles(
        tick_data: pd.DataFrame, interval: str
    ) -> List[Dict]
```

**Process:**
1. Fetch tick data from vnstock
2. Filter by date range
3. Resample to desired interval
4. Aggregate OHLCV data
5. Return list of candles

### 6.3 Market Screener (app/services/market_screener.py)

**Stock screening with filters**

```python
class MarketScreener:
    def screen_stocks(
        filters: Dict[str, Any],
        exchange: str = 'HOSE',
        limit: int = 50
    ) -> List[Dict]

    def get_preset_screens() -> Dict[str, Any]
```

**Available Filters:**
- `pe_min`, `pe_max`: P/E ratio range
- `pb_max`: P/B ratio max
- `roe_min`: ROE minimum
- `market_cap_min`: Market cap minimum
- `price_change_min/max`: Price change % (30d)
- `volume_min`: Volume minimum
- `rsi_min`, `rsi_max`: RSI range

**Preset Screeners:**
- `value_stocks`: Low P/E, high ROE
- `growth_stocks`: High revenue growth
- `oversold_stocks`: RSI < 30
- `dividend_stocks`: High dividend yield
- `breakout_stocks`: Price breakout patterns

### 6.4 Market Heatmap (app/services/market_heatmap.py)

**Market overview by sectors**

```python
class MarketHeatmap:
    def get_market_overview(exchange: str) -> Dict[str, Any]
    def get_industry_heatmap(sector: str, exchange: str) -> Dict[str, Any]
```

**Output:**
- Sectors performance
- Top gainers/losers
- Volume leaders
- Color-coded visualization data

### 6.5 Portfolio Analytics (app/services/portfolio_analytics.py)

**Portfolio analysis and optimization**

```python
class PortfolioAnalytics:
    def analyze_portfolio(
        holdings: List[Dict],
        period_days: int = 365
    ) -> Dict[str, Any]

    def compare_with_market(
        portfolio_return: float,
        period_days: int
    ) -> Dict[str, Any]
```

**Analysis Includes:**
- Portfolio summary (total value, P&L, return %)
- Risk metrics (volatility, VaR, Sharpe ratio, beta)
- Diversification (sector allocation, Herfindahl index)
- Performance (top/worst performers, annualized return)
- Optimization suggestions

### 6.6 News Aggregator (app/services/news_aggregator.py)

**News aggregation and sentiment analysis**

```python
class NewsAggregator:
    def get_latest_news(
        symbol?: str,
        limit: int = 20,
        sources: List[str] = ['mock']
    ) -> List[Dict]

    def get_market_sentiment_summary(days: int = 7) -> Dict[str, Any]

    def search_news(query: str, limit: int, days: int) -> List[Dict]
```

**Features:**
- Multi-source aggregation (cafef, vietstock, ndh, zing)
- Sentiment analysis
- Keyword search
- Date filtering

---

## 7. Deployment và Infrastructure

### 7.1 Docker Setup

#### Dockerfile

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  # VNStock API
  vnstock-api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: vnstock-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - PYTHONUNBUFFERED=1
      - HOME=/app
      - VNSTOCK_DATA_DIR=/app/.vnstock
    networks:
      - vnstock-network
    volumes:
      - ./logs:/app/logs
    labels:
      - "com.vnstock.description=VNStock API Service"

  # n8n Workflow Automation
  n8n:
    image: n8nio/n8n:latest
    container_name: n8n
    restart: unless-stopped
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=admin123
      - GENERIC_TIMEZONE=Asia/Ho_Chi_Minh
    networks:
      - vnstock-network
    volumes:
      - n8n_data:/home/node/.n8n
      - ./n8n/workflows:/home/node/.n8n/workflows
    depends_on:
      - vnstock-api

networks:
  vnstock-network:
    driver: bridge
    name: vnstock-network

volumes:
  n8n_data:
    name: n8n_data
    driver: local
```

### 7.2 Environment Variables

```bash
# .env file
# n8n Configuration
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=admin123
N8N_HOST=localhost
WEBHOOK_URL=http://localhost:5678/
TIMEZONE=Asia/Ho_Chi_Minh

# VNStock API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Database (optional)
DATABASE_URL=sqlite:///./vnstock.db

# Cache (optional)
CACHE_DEFAULT_TTL=300  # 5 minutes
```

### 7.3 Deployment Scripts

#### docker-start.sh
```bash
#!/bin/bash
docker-compose up -d
docker-compose logs -f
```

#### docker-stop.sh
```bash
#!/bin/bash
docker-compose down
```

#### docker-rebuild.sh
```bash
#!/bin/bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 7.4 Production Deployment

#### With Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /var/www/vnstock-frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # n8n
    location /n8n/ {
        proxy_pass http://localhost:5678/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### SSL with Certbot

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### 7.5 Monitoring & Logging

#### Application Logs

```python
# app/main.py
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

#### Docker Logs

```bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f vnstock-api
docker-compose logs -f n8n

# View last N lines
docker-compose logs --tail=100 vnstock-api
```

---

## 8. API Reference

### 8.1 Stock Data Endpoints

#### GET /api/stock/{symbol}

**Description**: Lấy toàn bộ dữ liệu cổ phiếu

**Parameters:**
- `symbol` (path, required): Mã cổ phiếu (VD: VNM, VCB, HPG)
- `start_date` (query, optional): Ngày bắt đầu (YYYY-MM-DD)
- `end_date` (query, optional): Ngày kết thúc (YYYY-MM-DD)

**Response:**
```json
{
  "symbol": "VNM",
  "company_info": {
    "company_name": "Vinamilk",
    "exchange": "HOSE",
    "industry": "Food & Beverage",
    "market_cap": 150000000000000
  },
  "price_data": [
    {
      "time": "2024-01-01",
      "open": 75000,
      "high": 76000,
      "low": 74500,
      "close": 75500,
      "volume": 1000000
    }
  ],
  "technical_indicators": {
    "SMA": { "SMA_20": [...], "SMA_50": [...] },
    "RSI": { "RSI_14": 65.5 },
    "MACD": { "MACD": [...], "Signal": [...] }
  },
  "fundamental_indicators": {
    "EPS": 5000,
    "PE": 15.2,
    "ROE": 25.5,
    "PB": 3.2
  },
  "metadata": {
    "total_records": 250,
    "current_price": 75500,
    "last_updated": "2024-01-31T10:30:00"
  }
}
```

**Example:**
```bash
curl "http://localhost:8000/api/stock/VNM?start_date=2024-01-01&end_date=2024-01-31"
```

---

#### GET /api/stock/{symbol}/intraday

**Description**: Lấy dữ liệu nến intraday

**Parameters:**
- `symbol` (path, required): Mã cổ phiếu
- `interval` (query, required): Khung thời gian (1m, 5m, 15m, 30m, 1h, 3h, 6h, 1d)
- `start_date` (query, optional): Ngày bắt đầu
- `end_date` (query, optional): Ngày kết thúc
- `limit` (query, optional): Số lượng tick tối đa (default: 5000)

**Response:**
```json
{
  "symbol": "VNM",
  "interval": "5m",
  "data": [
    {
      "time": "2024-01-31T09:00:00",
      "open": 75000,
      "high": 75200,
      "low": 74900,
      "close": 75100,
      "volume": 50000
    }
  ],
  "total_candles": 78,
  "cached": false
}
```

**Example:**
```bash
curl "http://localhost:8000/api/stock/VNM/intraday?interval=5m&limit=1000"
```

---

#### GET /api/stock/{symbol}/candlestick-patterns

**Description**: Nhận dạng mô hình nến Nhật

**Parameters:**
- `symbol` (path, required): Mã cổ phiếu
- `start_date` (query, optional): Ngày bắt đầu
- `end_date` (query, optional): Ngày kết thúc
- `latest_n` (query, optional): Lấy N mô hình gần nhất

**Response:**
```json
{
  "symbol": "VNM",
  "patterns": [
    {
      "date": "2024-01-15",
      "pattern": "Bullish Engulfing",
      "signal": "buy",
      "strength": "strong",
      "description": "Mô hình nhấn chìm tăng - tín hiệu mua mạnh"
    },
    {
      "date": "2024-01-20",
      "pattern": "Doji",
      "signal": "neutral",
      "strength": "weak",
      "description": "Mô hình do dự - cần chờ xác nhận"
    }
  ],
  "total": 15
}
```

**Supported Patterns:**
- Doji, Hammer, Inverted Hammer, Shooting Star
- Bullish/Bearish Engulfing
- Morning Star, Evening Star
- Three White Soldiers, Three Black Crows
- Bullish/Bearish Harami

---

### 8.2 Market Screener Endpoints

#### POST /api/screener/scan

**Description**: Quét cổ phiếu theo bộ lọc tùy chỉnh

**Request Body:**
```json
{
  "pe_max": 15,
  "pb_max": 2,
  "roe_min": 15,
  "market_cap_min": 1000000000000
}
```

**Parameters:**
- `exchange` (query): Sàn giao dịch (HOSE, HNX, UPCOM, ALL)
- `limit` (query): Số lượng cổ phiếu tối đa

**Response:**
```json
{
  "success": true,
  "exchange": "HOSE",
  "filters_applied": { "pe_max": 15, "roe_min": 15 },
  "total_found": 25,
  "stocks": [
    {
      "symbol": "VNM",
      "company_name": "Vinamilk",
      "price": 75500,
      "pe": 14.5,
      "pb": 3.2,
      "roe": 25.5,
      "market_cap": 150000000000000,
      "score": 85.5
    }
  ]
}
```

---

#### GET /api/screener/preset/{preset_name}

**Description**: Quét cổ phiếu theo preset có sẵn

**Available Presets:**
- `value_stocks`: Cổ phiếu giá trị
- `growth_stocks`: Cổ phiếu tăng trưởng
- `oversold_stocks`: Cổ phiếu quá bán
- `dividend_stocks`: Cổ phiếu cổ tức
- `breakout_stocks`: Cổ phiếu breakout

**Example:**
```bash
curl "http://localhost:8000/api/screener/preset/value_stocks?exchange=HOSE&limit=50"
```

---

### 8.3 Portfolio Analytics Endpoints

#### POST /api/portfolio/analyze

**Description**: Phân tích danh mục đầu tư

**Request Body:**
```json
[
  {
    "symbol": "VNM",
    "quantity": 100,
    "buy_price": 55000
  },
  {
    "symbol": "VIC",
    "quantity": 200,
    "buy_price": 40000
  }
]
```

**Response:**
```json
{
  "success": true,
  "data": {
    "portfolio_summary": {
      "total_value": 15000000,
      "total_cost": 13500000,
      "total_pnl": 1500000,
      "total_return_pct": 11.11
    },
    "risk_metrics": {
      "volatility": 18.5,
      "var_95": 250000,
      "sharpe_ratio": 1.25,
      "beta": 0.95
    },
    "diversification": {
      "sector_allocation": {
        "Food & Beverage": 36.7,
        "Real Estate": 53.3,
        "Other": 10.0
      },
      "herfindahl_index": 0.45
    },
    "performance": {
      "top_performers": [...],
      "worst_performers": [...],
      "annualized_return": 13.5
    },
    "recommendations": [
      "Consider rebalancing - Food & Beverage sector is overweight",
      "Add more defensive stocks to reduce volatility"
    ]
  }
}
```

---

### 8.4 Cache Management Endpoints

#### GET /api/cache/stats

**Description**: Lấy thống kê cache

**Response:**
```json
{
  "success": true,
  "stats": {
    "size": 128,
    "hits": 1250,
    "misses": 350,
    "hit_rate": 78.12,
    "total_requests": 1600
  }
}
```

---

#### POST /api/cache/clear

**Description**: Xóa toàn bộ cache

**Response:**
```json
{
  "success": true,
  "message": "Cache cleared successfully"
}
```

---

### 8.5 Admin Endpoints

#### POST /api/admin/api-keys/create

**Description**: Tạo API key mới (Admin only)

**Headers:**
```
X-API-Key: dev_key_12345
```

**Request Body:**
```json
{
  "name": "My Application",
  "tier": "pro"
}
```

**Response:**
```json
{
  "success": true,
  "api_key": "vnstock_abc123def456ghi789",
  "tier": "pro",
  "tier_config": {
    "max_requests_per_minute": 300,
    "max_requests_per_day": 20000
  },
  "message": "API key created successfully. Keep this key secret!",
  "usage": "Add header: X-API-Key: vnstock_abc123def456ghi789"
}
```

---

## 9. Development Guide

### 9.1 Local Development Setup

#### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

#### Backend Setup

```bash
# Clone repository
cd vnstock-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use script
./run.sh
```

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm start

# Build for production
npm run build
```

### 9.2 Adding New Endpoints

**Step 1: Create Pydantic Schema** (app/models/schemas.py)
```python
class NewFeatureRequest(BaseModel):
    param1: str
    param2: int

class NewFeatureResponse(BaseModel):
    result: Dict[str, Any]
```

**Step 2: Create Service** (app/services/new_service.py)
```python
class NewService:
    def process_data(self, param1, param2):
        # Business logic here
        return result
```

**Step 3: Add Route** (app/api/routes.py)
```python
@router.post("/api/new-feature")
async def new_feature(request: NewFeatureRequest):
    service = NewService()
    result = service.process_data(request.param1, request.param2)
    return {"result": result}
```

**Step 4: Test Endpoint**
```bash
curl -X POST http://localhost:8000/api/new-feature \
  -H "Content-Type: application/json" \
  -d '{"param1": "test", "param2": 123}'
```

### 9.3 Adding New Technical Indicators

**File**: app/utils/technical_indicators.py

```python
class TechnicalAnalyzer:
    def calculate_new_indicator(self, period: int = 14) -> Dict[str, Any]:
        """
        Calculate new technical indicator

        Args:
            period: Lookback period

        Returns:
            Dictionary with indicator values
        """
        if len(self.df) >= period:
            # Your calculation here
            values = self.df['close'].rolling(window=period).mean()
            return {
                'NEW_INDICATOR': values.fillna(0).tolist()
            }
        return {}

    def calculate_all_indicators(self):
        """Add to this method"""
        result = {
            # ... existing indicators
            'NEW_INDICATOR': self.calculate_new_indicator()
        }
        return result
```

### 9.4 Testing

#### Backend Tests

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_stock_data():
    response = client.get("/api/stock/VNM")
    assert response.status_code == 200
    assert "symbol" in response.json()
    assert response.json()["symbol"] == "VNM"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```

Run tests:
```bash
pytest tests/ -v
```

#### Frontend Tests

```typescript
// src/App.test.tsx
import { render, screen } from '@testing-library/react';
import App from './App';

test('renders app header', () => {
  render(<App />);
  const headerElement = screen.getByText(/VNStock Trading/i);
  expect(headerElement).toBeInTheDocument();
});
```

Run tests:
```bash
cd frontend
npm test
```

---

## 10. Troubleshooting

### 10.1 Common Issues

#### Issue: "ModuleNotFoundError: No module named 'vnstock'"

**Solution:**
```bash
pip install git+https://github.com/thinh-vu/vnstock.git
```

---

#### Issue: "Database is locked"

**Solution:**
```python
# Increase timeout in database.py
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30}
)
```

---

#### Issue: "Rate limit exceeded"

**Solution:**
- Check your API tier limits
- Implement exponential backoff
- Upgrade to higher tier

```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RateLimitError:
                    if i < max_retries - 1:
                        time.sleep(2 ** i)  # Exponential backoff
                    else:
                        raise
        return wrapper
    return decorator
```

---

#### Issue: "CORS error in browser"

**Solution:**
```python
# app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specific origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

#### Issue: "Docker container exits immediately"

**Solution:**
```bash
# Check logs
docker-compose logs vnstock-api

# Common fixes:
# 1. Check Dockerfile syntax
# 2. Verify requirements.txt
# 3. Check port conflicts
docker ps -a  # See all containers
lsof -i :8000  # Check port usage
```

---

### 10.2 Performance Optimization

#### Backend Optimization

**1. Database Indexing**
```python
# Add indexes to frequently queried columns
Index('idx_symbol_date', 'symbol', 'date')
```

**2. Batch Processing**
```python
# Process multiple stocks in batch
async def batch_update_stocks(symbols: List[str]):
    tasks = [update_stock(symbol) for symbol in symbols]
    await asyncio.gather(*tasks)
```

**3. Connection Pooling**
```python
# Use connection pool
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

#### Frontend Optimization

**1. Code Splitting**
```typescript
// Lazy load components
const MarketScreener = lazy(() => import('./components/MarketScreener'));
```

**2. Memoization**
```typescript
const memoizedValue = useMemo(() =>
  computeExpensiveValue(a, b),
  [a, b]
);
```

**3. Virtual Scrolling**
```typescript
// For large lists
import { FixedSizeList } from 'react-window';
```

---

### 10.3 Security Best Practices

**1. API Key Management**
- Never commit API keys to version control
- Use environment variables
- Rotate keys regularly

**2. Input Validation**
```python
from pydantic import validator

class StockRequest(BaseModel):
    symbol: str

    @validator('symbol')
    def symbol_must_be_valid(cls, v):
        if not v.isupper() or len(v) < 3:
            raise ValueError('Invalid symbol format')
        return v
```

**3. Rate Limiting**
```python
# Implement rate limiting per user/IP
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/stock/{symbol}")
@limiter.limit("5/minute")
async def get_stock(symbol: str):
    ...
```

**4. SQL Injection Prevention**
```python
# Always use ORM or parameterized queries
# SQLAlchemy automatically prevents SQL injection
db.query(Stock).filter(Stock.symbol == symbol).first()
```

---

## Kết Luận

VNStock API là một hệ thống phân tích chứng khoán hoàn chỉnh với:

✅ **Backend mạnh mẽ**: FastAPI + vnstock + SQLAlchemy
✅ **Frontend hiện đại**: React + TypeScript + Lightweight Charts
✅ **Containerization**: Docker ready
✅ **Production ready**: Rate limiting, caching, authentication
✅ **Extensible**: Dễ dàng mở rộng với các tính năng mới

### Resources

- **Repository**: https://github.com/thinh-vu/vnstock
- **Documentation**: http://localhost:8000/docs
- **API Docs**: http://localhost:8000/redoc
- **n8n**: http://localhost:5678

### Support

Để được hỗ trợ, vui lòng:
1. Kiểm tra tài liệu này
2. Xem API documentation tại /docs
3. Tạo issue trên GitHub
4. Liên hệ team qua email

---

**Phiên bản tài liệu**: 1.0.0
**Cập nhật lần cuối**: November 2025
**Tác giả**: VNStock Development Team
