"""
API Routes cho vnstock API
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import Optional, List, Dict, Any
from ..models.schemas import StockRequest, StockResponse
from ..services.vnstock_service import VNStockService
from ..services.market_screener import MarketScreener
from ..services.market_heatmap import MarketHeatmap
from ..services.portfolio_analytics import PortfolioAnalytics
from ..services.news_aggregator import NewsAggregator
from ..services.intraday_service import IntradayService
from ..core.cache import get_cache

router = APIRouter()


@router.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "VNStock API - Vietnam Stock Market Data API",
        "version": "1.0.0",
        "documentation": "/docs",
        "endpoints": {
            "/api/stock/{symbol}": "Lấy toàn bộ dữ liệu cổ phiếu",
            "/api/stock/{symbol}/price": "Lấy dữ liệu giá",
            "/api/stock/{symbol}/technical": "Lấy chỉ số kỹ thuật",
            "/api/stock/{symbol}/fundamental": "Lấy chỉ số cơ bản",
            "/api/stock/{symbol}/company": "Lấy thông tin công ty"
        }
    }


@router.get("/api/stock/{symbol}", response_model=StockResponse)
async def get_stock_data(
    symbol: str,
    start_date: Optional[str] = Query(
        None,
        description="Ngày bắt đầu (YYYY-MM-DD). Nếu không cung cấp sẽ lấy từ ngày niêm yết",
        example="2024-01-01"
    ),
    end_date: Optional[str] = Query(
        None,
        description="Ngày kết thúc (YYYY-MM-DD). Nếu không cung cấp sẽ lấy đến ngày hiện tại",
        example="2024-12-31"
    )
):
    """
    Lấy toàn bộ dữ liệu cổ phiếu bao gồm:
    - Thông tin công ty
    - Dữ liệu giá lịch sử
    - Các chỉ số kỹ thuật (SMA, EMA, MACD, RSI, BB, ATR, OBV, Ichimoku, PSAR, MFI, A/D, CMF, ADL)
    - Các chỉ số cơ bản (EPS, P/E, P/B, P/S, ROE, ROA, D/E, CR, NPM, RG, OCF, FCF)
    - Các chỉ số vĩ mô (GDP, CPI, IR, EXR, UR, FGI, PCR)

    **Ví dụ sử dụng với curl:**

    ```bash
    # Lấy dữ liệu VNM trong khoảng thời gian cụ thể
    curl "http://localhost:8000/api/stock/VNM?start_date=2024-01-01&end_date=2024-01-31"

    # Lấy dữ liệu VCB từ đầu năm đến hiện tại
    curl "http://localhost:8000/api/stock/VCB?start_date=2024-01-01"

    # Lấy dữ liệu HPG 5 năm gần nhất (không cần tham số)
    curl "http://localhost:8000/api/stock/HPG"
    ```

    **Ví dụ import vào HTTP Request tool (n8n, Postman, etc.):**

    ```
    GET http://localhost:8000/api/stock/VNM?start_date=2024-01-01&end_date=2024-01-31
    ```

    Args:
        symbol: Mã cổ phiếu (VD: VNM, VCB, HPG)
        start_date: Ngày bắt đầu (YYYY-MM-DD)
        end_date: Ngày kết thúc (YYYY-MM-DD)

    Returns:
        Toàn bộ dữ liệu cổ phiếu dưới dạng JSON
    """
    try:
        service = VNStockService()
        data = service.get_complete_stock_data(symbol.upper(), start_date, end_date)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting stock data: {str(e)}")


@router.get("/api/stock/{symbol}/price")
async def get_price_data(
    symbol: str,
    start_date: Optional[str] = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)", example="2024-01-01"),
    end_date: Optional[str] = Query(None, description="Ngày kết thúc (YYYY-MM-DD)", example="2024-12-31")
):
    """
    Lấy dữ liệu giá lịch sử của cổ phiếu

    **Curl examples:**
    ```bash
    curl "http://localhost:8000/api/stock/VNM/price?start_date=2024-01-01&end_date=2024-01-31"
    curl "http://localhost:8000/api/stock/VCB/price"
    ```

    **HTTP Request:**
    ```
    GET http://localhost:8000/api/stock/VNM/price?start_date=2024-01-01&end_date=2024-01-31
    ```

    Args:
        symbol: Mã cổ phiếu
        start_date: Ngày bắt đầu
        end_date: Ngày kết thúc

    Returns:
        Dữ liệu giá dưới dạng JSON
    """
    try:
        service = VNStockService()
        df = service.get_price_data(symbol.upper(), start_date, end_date)
        price_data = df.reset_index().to_dict('records')

        # Chuyển đổi timestamp sang string
        for record in price_data:
            for key, value in record.items():
                if hasattr(value, 'strftime'):
                    record[key] = value.strftime('%Y-%m-%d')

        return {
            'symbol': symbol.upper(),
            'data': price_data,
            'total_records': len(price_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting price data: {str(e)}")


@router.get("/api/stock/{symbol}/intraday")
async def get_intraday_data(
    symbol: str,
    interval: str = Query(
        '5m',
        description="Khung thời gian (1m, 5m, 15m, 30m, 1h, 3h, 6h, 1d)",
        example="5m"
    ),
    start_date: Optional[str] = Query(
        None,
        description="Ngày bắt đầu (YYYY-MM-DD)",
        example="2024-01-01"
    ),
    end_date: Optional[str] = Query(
        None,
        description="Ngày kết thúc (YYYY-MM-DD)",
        example="2024-01-31"
    ),
    limit: int = Query(
        5000,
        description="Số lượng tick tối đa",
        ge=100,
        le=10000
    )
):
    """
    Lấy dữ liệu nến intraday của cổ phiếu với các khung thời gian ngắn

    Hỗ trợ các khung thời gian:
    - 1m: 1 phút
    - 5m: 5 phút
    - 15m: 15 phút
    - 30m: 30 phút
    - 1h: 1 giờ
    - 3h: 3 giờ
    - 6h: 6 giờ
    - 1d: 1 ngày

    **Curl examples:**
    ```bash
    curl "http://localhost:8000/api/stock/VNM/intraday?interval=5m&limit=1000"
    curl "http://localhost:8000/api/stock/VCB/intraday?interval=1h&start_date=2024-01-01"
    ```

    Args:
        symbol: Mã cổ phiếu
        interval: Khung thời gian
        start_date: Ngày bắt đầu
        end_date: Ngày kết thúc
        limit: Số lượng tick tối đa để xử lý

    Returns:
        Dữ liệu nến intraday dưới dạng JSON với OHLCV
    """
    try:
        # Create cache key
        cache_key = f"intraday_{symbol}_{interval}_{start_date}_{end_date}_{limit}"
        cache = get_cache()

        # Try to get from cache
        cached_data = cache.get(cache_key)
        if cached_data:
            return {
                'symbol': symbol.upper(),
                'interval': interval,
                'data': cached_data,
                'total_candles': len(cached_data),
                'cached': True
            }

        # Get intraday data
        service = IntradayService(source='VCI')
        candles = service.get_intraday_candles(
            symbol=symbol.upper(),
            interval=interval,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )

        # Cache for 1 minute (intraday data changes frequently)
        cache.set(cache_key, candles, ttl=60)

        return {
            'symbol': symbol.upper(),
            'interval': interval,
            'data': candles,
            'total_candles': len(candles),
            'cached': False
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting intraday data: {str(e)}")


@router.get("/api/stock/{symbol}/intervals")
async def get_supported_intervals():
    """
    Lấy danh sách các khung thời gian được hỗ trợ

    Returns:
        List của các interval được hỗ trợ
    """
    try:
        service = IntradayService()
        intervals = service.get_supported_intervals()
        return {
            'intervals': intervals,
            'descriptions': {
                '1m': '1 phút',
                '5m': '5 phút',
                '15m': '15 phút',
                '30m': '30 phút',
                '1h': '1 giờ',
                '3h': '3 giờ',
                '6h': '6 giờ',
                '1d': '1 ngày'
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting intervals: {str(e)}")


@router.get("/api/stock/{symbol}/technical")
async def get_technical_indicators(
    symbol: str,
    start_date: Optional[str] = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)", example="2024-01-01"),
    end_date: Optional[str] = Query(None, description="Ngày kết thúc (YYYY-MM-DD)", example="2024-12-31")
):
    """
    Lấy các chỉ số kỹ thuật của cổ phiếu (SMA, EMA, MACD, RSI, Bollinger Bands, ATR, OBV, Ichimoku, PSAR, MFI, A/D, CMF, ADL)

    **Curl examples:**
    ```bash
    curl "http://localhost:8000/api/stock/VNM/technical?start_date=2024-01-01&end_date=2024-01-31"
    curl "http://localhost:8000/api/stock/HPG/technical"
    ```

    **HTTP Request:**
    ```
    GET http://localhost:8000/api/stock/VNM/technical?start_date=2024-01-01&end_date=2024-01-31
    ```

    Args:
        symbol: Mã cổ phiếu
        start_date: Ngày bắt đầu
        end_date: Ngày kết thúc

    Returns:
        Các chỉ số kỹ thuật dưới dạng JSON
    """
    try:
        service = VNStockService()
        df = service.get_price_data(symbol.upper(), start_date, end_date)

        from ..utils.technical_indicators import TechnicalAnalyzer
        analyzer = TechnicalAnalyzer(df)
        indicators = analyzer.calculate_all_indicators()

        return {
            'symbol': symbol.upper(),
            'indicators': indicators
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting technical indicators: {str(e)}")


@router.get("/api/stock/{symbol}/fundamental")
async def get_fundamental_indicators(symbol: str):
    """
    Lấy các chỉ số cơ bản của cổ phiếu (EPS, P/E, P/B, P/S, ROE, ROA, D/E, CR, NPM, RG, OCF, FCF)

    **Curl examples:**
    ```bash
    curl "http://localhost:8000/api/stock/VNM/fundamental"
    curl "http://localhost:8000/api/stock/VCB/fundamental"
    ```

    **HTTP Request:**
    ```
    GET http://localhost:8000/api/stock/VNM/fundamental
    ```

    Args:
        symbol: Mã cổ phiếu

    Returns:
        Các chỉ số cơ bản dưới dạng JSON
    """
    try:
        service = VNStockService()

        # Lấy thông tin công ty
        company_info = service.get_company_info(symbol.upper())

        # Lấy dữ liệu giá hiện tại
        df = service.get_price_data(symbol.upper())
        current_price = float(df['close'].iloc[-1]) if not df.empty else 0

        # Lấy báo cáo tài chính
        financial_statements = service.get_financial_statements(symbol.upper())

        # Tính các chỉ số
        from ..utils.fundamental_indicators import FundamentalAnalyzer
        shares_outstanding = company_info.get('shares_outstanding', 1000000)
        market_cap = company_info.get('market_cap', current_price * shares_outstanding)

        analyzer = FundamentalAnalyzer(financial_statements)
        indicators = analyzer.calculate_all_indicators(current_price, shares_outstanding, market_cap)

        return {
            'symbol': symbol.upper(),
            'indicators': indicators,
            'current_price': current_price
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting fundamental indicators: {str(e)}")


@router.get("/api/stock/{symbol}/company")
async def get_company_info(symbol: str):
    """
    Lấy thông tin công ty (tên, sàn, ngành, website, mô tả...)

    **Curl examples:**
    ```bash
    curl "http://localhost:8000/api/stock/VNM/company"
    curl "http://localhost:8000/api/stock/HPG/company"
    ```

    **HTTP Request:**
    ```
    GET http://localhost:8000/api/stock/VNM/company
    ```

    Args:
        symbol: Mã cổ phiếu

    Returns:
        Thông tin công ty dưới dạng JSON
    """
    try:
        service = VNStockService()
        company_info = service.get_company_info(symbol.upper())
        return company_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting company info: {str(e)}")


@router.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "service": "vnstock-api"
    }


# ==================== MARKET SCREENER ENDPOINTS ====================

@router.post("/api/screener/scan")
async def screen_stocks(
    filters: Dict[str, Any] = Body(..., example={
        "pe_max": 15,
        "pb_max": 2,
        "roe_min": 15,
        "market_cap_min": 1000000000000
    }),
    exchange: str = Query("HOSE", description="Sàn giao dịch: HOSE, HNX, UPCOM, ALL"),
    limit: int = Query(50, description="Số lượng cổ phiếu tối đa")
):
    """
    Quét cổ phiếu theo bộ lọc tùy chỉnh

    **Các bộ lọc có sẵn:**
    - `pe_min`, `pe_max`: P/E ratio
    - `pb_max`: P/B ratio
    - `roe_min`: ROE (%)
    - `market_cap_min`: Vốn hóa tối thiểu (VND)
    - `price_change_min`, `price_change_max`: % thay đổi giá (30 ngày)
    - `volume_min`: Khối lượng giao dịch tối thiểu
    - `rsi_min`, `rsi_max`: RSI indicator
    """
    try:
        screener = MarketScreener()
        results = screener.screen_stocks(filters, exchange, limit)

        return {
            "success": True,
            "exchange": exchange,
            "filters_applied": filters,
            "total_found": len(results),
            "stocks": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/screener/presets")
async def get_preset_screens():
    """
    Lấy danh sách các bộ lọc preset

    **Presets:**
    - `value_stocks`: Cổ phiếu giá trị
    - `growth_stocks`: Cổ phiếu tăng trưởng
    - `oversold_stocks`: Cổ phiếu quá bán
    - `dividend_stocks`: Cổ phiếu cổ tức
    - `breakout_stocks`: Cổ phiếu breakout
    """
    try:
        screener = MarketScreener()
        presets = screener.get_preset_screens()

        return {
            "success": True,
            "presets": presets
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/screener/preset/{preset_name}")
async def screen_by_preset(
    preset_name: str,
    exchange: str = Query("HOSE", description="Sàn giao dịch"),
    limit: int = Query(50, description="Số lượng cổ phiếu")
):
    """
    Quét cổ phiếu theo preset có sẵn
    """
    try:
        screener = MarketScreener()
        presets = screener.get_preset_screens()

        if preset_name not in presets:
            raise HTTPException(
                status_code=404,
                detail=f"Preset '{preset_name}' không tồn tại. Các preset hợp lệ: {list(presets.keys())}"
            )

        preset = presets[preset_name]
        results = screener.screen_stocks(preset['filters'], exchange, limit)

        return {
            "success": True,
            "preset": preset,
            "exchange": exchange,
            "total_found": len(results),
            "stocks": results
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== MARKET HEATMAP ENDPOINTS ====================

@router.get("/api/heatmap/market")
async def get_market_heatmap(
    exchange: str = Query("HOSE", description="Sàn giao dịch: HOSE, HNX, UPCOM")
):
    """
    Lấy heatmap toàn thị trường theo sectors

    Trả về dữ liệu thị trường được nhóm theo ngành,
    hiển thị tình hình tăng/giảm của từng ngành
    """
    try:
        heatmap = MarketHeatmap()
        data = heatmap.get_market_overview(exchange)

        return {
            "success": True,
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/heatmap/sector/{sector}")
async def get_sector_heatmap(
    sector: str,
    exchange: str = Query("HOSE", description="Sàn giao dịch")
):
    """
    Lấy heatmap chi tiết cho một ngành cụ thể
    """
    try:
        heatmap = MarketHeatmap()
        data = heatmap.get_industry_heatmap(sector, exchange)

        if 'error' in data:
            raise HTTPException(status_code=404, detail=data['error'])

        return {
            "success": True,
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== PORTFOLIO ANALYTICS ENDPOINTS ====================

@router.post("/api/portfolio/analyze")
async def analyze_portfolio(
    holdings: List[Dict[str, Any]] = Body(..., example=[
        {"symbol": "VNM", "quantity": 100, "buy_price": 55000},
        {"symbol": "VIC", "quantity": 200, "buy_price": 40000}
    ]),
    period_days: int = Query(365, description="Số ngày phân tích")
):
    """
    Phân tích danh mục đầu tư

    **Input:** Danh sách cổ phiếu đang nắm giữ

    **Output:**
    - Tổng quan danh mục (vốn, lời/lỗ, tỷ suất sinh lời)
    - Phân tích rủi ro (volatility, VaR, Sharpe ratio, beta)
    - Đa dạng hóa (phân bổ theo ngành, Herfindahl index)
    - Hiệu suất (top/worst performers, annualized return)
    - Đề xuất tối ưu danh mục
    """
    try:
        if not holdings:
            raise HTTPException(status_code=400, detail="Danh mục trống")

        analytics = PortfolioAnalytics()
        result = analytics.analyze_portfolio(holdings, period_days)

        if 'error' in result:
            raise HTTPException(status_code=400, detail=result['error'])

        return {
            "success": True,
            "data": result
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/portfolio/compare-market")
async def compare_with_market(
    portfolio_return: float = Query(..., description="Tỷ suất sinh lời danh mục (%)"),
    period_days: int = Query(365, description="Số ngày")
):
    """
    So sánh hiệu suất danh mục với thị trường (VN-Index)
    """
    try:
        analytics = PortfolioAnalytics()
        result = analytics.compare_with_market(portfolio_return, period_days)

        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== NEWS AGGREGATOR ENDPOINTS ====================

@router.get("/api/news/latest")
async def get_latest_news(
    symbol: Optional[str] = Query(None, description="Mã cổ phiếu (để trống = tin tổng hợp)"),
    limit: int = Query(20, description="Số lượng tin tức"),
    sources: Optional[List[str]] = Query(None, description="Danh sách nguồn tin")
):
    """
    Lấy tin tức mới nhất

    **Nguồn tin:**
    - cafef
    - vietstock
    - ndh
    - zing
    """
    try:
        if sources is None:
            sources = ['mock']  # Use mock data for now

        aggregator = NewsAggregator()
        news = aggregator.get_latest_news(symbol, limit, sources)

        return {
            "success": True,
            "symbol": symbol,
            "total": len(news),
            "news": news
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/news/sentiment")
async def get_market_sentiment(
    days: int = Query(7, description="Số ngày phân tích")
):
    """
    Tổng hợp tâm lý thị trường từ tin tức

    Phân tích sentiment của tin tức trong N ngày gần nhất
    để đánh giá tâm lý chung của thị trường
    """
    try:
        aggregator = NewsAggregator()
        sentiment = aggregator.get_market_sentiment_summary(days)

        return {
            "success": True,
            "data": sentiment
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/news/search")
async def search_news(
    query: str = Query(..., description="Từ khóa tìm kiếm"),
    limit: int = Query(20, description="Số lượng tin tức"),
    days: int = Query(30, description="Tìm trong N ngày gần nhất")
):
    """
    Tìm kiếm tin tức theo từ khóa
    """
    try:
        aggregator = NewsAggregator()
        news = aggregator.search_news(query, limit, days)

        return {
            "success": True,
            "query": query,
            "total": len(news),
            "news": news
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CANDLESTICK PATTERNS ENDPOINTS ====================

@router.get("/api/stock/{symbol}/candlestick-patterns")
async def get_candlestick_patterns(
    symbol: str,
    start_date: Optional[str] = Query(None, description="Ngày bắt đầu (YYYY-MM-DD)", example="2024-01-01"),
    end_date: Optional[str] = Query(None, description="Ngày kết thúc (YYYY-MM-DD)", example="2024-12-31"),
    latest_n: Optional[int] = Query(None, description="Lấy N mô hình gần nhất", example=10)
):
    """
    Nhận dạng các mô hình nến Nhật (Japanese Candlestick Patterns)

    **Các mô hình được hỗ trợ:**
    - **Doji**: Nến có body rất nhỏ, biểu hiện sự do dự
    - **Hammer**: Búa - tín hiệu đảo chiều tăng
    - **Inverted Hammer**: Búa ngược - tín hiệu đảo chiều tăng
    - **Shooting Star**: Sao băng - tín hiệu đảo chiều giảm
    - **Bullish Engulfing**: Nhấn chìm tăng - tín hiệu mua mạnh
    - **Bearish Engulfing**: Nhấn chìm giảm - tín hiệu bán mạnh
    - **Morning Star**: Sao mai - tín hiệu đảo chiều tăng (3 nến)
    - **Evening Star**: Sao hôm - tín hiệu đảo chiều giảm (3 nến)
    - **Three White Soldiers**: Ba người lính - xu hướng tăng mạnh
    - **Three Black Crows**: Ba con quạ - xu hướng giảm mạnh
    - **Bullish Harami**: Mang thai tăng - tín hiệu đảo chiều tăng
    - **Bearish Harami**: Mang thai giảm - tín hiệu đảo chiều giảm

    **Curl examples:**
    ```bash
    # Lấy tất cả mô hình
    curl "http://localhost:8000/api/stock/VNM/candlestick-patterns?start_date=2024-01-01&end_date=2024-12-31"

    # Lấy 10 mô hình gần nhất
    curl "http://localhost:8000/api/stock/VNM/candlestick-patterns?latest_n=10"
    ```

    **HTTP Request:**
    ```
    GET http://localhost:8000/api/stock/VNM/candlestick-patterns?start_date=2024-01-01&end_date=2024-12-31
    ```

    Args:
        symbol: Mã cổ phiếu
        start_date: Ngày bắt đầu
        end_date: Ngày kết thúc
        latest_n: Lấy N mô hình gần nhất (tùy chọn)

    Returns:
        Các mô hình nến được phát hiện dưới dạng JSON
    """
    try:
        service = VNStockService()
        df = service.get_price_data(symbol.upper(), start_date, end_date)

        from ..utils.candlestick_patterns import CandlestickPatternDetector
        detector = CandlestickPatternDetector(df)

        if latest_n:
            patterns = detector.get_latest_patterns(latest_n)
            return {
                'symbol': symbol.upper(),
                'patterns': patterns,
                'total': len(patterns)
            }
        else:
            all_patterns = detector.detect_all_patterns()
            return {
                'symbol': symbol.upper(),
                'patterns': all_patterns
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting candlestick patterns: {str(e)}")


# ==================== CACHE MANAGEMENT ENDPOINTS ====================

@router.get("/api/cache/stats")
async def get_cache_stats():
    """
    Lấy thống kê cache

    Returns:
        Thống kê về cache (size, hits, misses, hit rate)
    """
    try:
        cache = get_cache()
        stats = cache.get_stats()

        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/cache/clear")
async def clear_cache():
    """
    Xóa toàn bộ cache

    Returns:
        Kết quả xóa cache
    """
    try:
        cache = get_cache()
        cache.clear()

        return {
            "success": True,
            "message": "Cache cleared successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/cache/cleanup")
async def cleanup_cache():
    """
    Dọn dẹp các cache entries đã hết hạn

    Returns:
        Số lượng entries đã bị xóa
    """
    try:
        cache = get_cache()
        removed = cache.cleanup_expired()

        return {
            "success": True,
            "removed": removed,
            "message": f"Removed {removed} expired cache entries"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== DATABASE & SCHEDULER ENDPOINTS ====================

@router.get("/api/admin/scheduler/status")
async def get_scheduler_status():
    """
    Lấy trạng thái scheduler và các jobs đang chạy

    Returns:
        Trạng thái scheduler và danh sách jobs
    """
    try:
        from ..scheduler import get_scheduler_status
        status = get_scheduler_status()

        return {
            "success": True,
            "scheduler": status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/admin/database/populate")
async def populate_database(
    exchange: str = Query("HOSE", description="Sàn giao dịch: HOSE, HNX, UPCOM"),
    delay_seconds: int = Query(3, description="Delay giữa các request (giây)", ge=1, le=10)
):
    """
    Populate database với dữ liệu ban đầu

    **Cảnh báo:** Job này có thể chạy lâu (30-60 phút) do rate limit.
    Nên chạy trong background hoặc khi thị trường đóng cửa.

    Args:
        exchange: Sàn giao dịch cần scan
        delay_seconds: Thời gian delay giữa các request để tránh rate limit

    Returns:
        Kết quả populate database
    """
    try:
        from ..scheduler.stock_updater import stock_updater

        # Run in background (non-blocking)
        import threading
        def run_populate():
            try:
                stock_updater.scan_all_symbols(exchange=exchange, delay_seconds=delay_seconds)
            except Exception as e:
                print(f"Error in populate job: {e}")

        thread = threading.Thread(target=run_populate, daemon=True)
        thread.start()

        return {
            "success": True,
            "message": f"Database population started for {exchange}",
            "info": "Job is running in background. Check job logs for progress.",
            "estimated_time": "30-60 minutes depending on rate limits"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/api/admin/database/update-stale")
async def update_stale_stocks(
    max_stocks: int = Query(50, description="Số lượng cổ phiếu tối đa", ge=1, le=200),
    max_age_hours: int = Query(24, description="Tuổi dữ liệu tối đa (giờ)", ge=1, le=168),
    delay_seconds: int = Query(3, description="Delay giữa các request (giây)", ge=1, le=10)
):
    """
    Cập nhật các cổ phiếu có dữ liệu cũ

    Args:
        max_stocks: Số lượng cổ phiếu tối đa cần update
        max_age_hours: Cập nhật các stocks có dữ liệu cũ hơn N giờ
        delay_seconds: Delay giữa các request

    Returns:
        Kết quả update
    """
    try:
        from ..scheduler.stock_updater import stock_updater

        # Run in background
        import threading
        def run_update():
            try:
                stock_updater.update_stale_stocks(
                    max_stocks=max_stocks,
                    delay_seconds=delay_seconds
                )
            except Exception as e:
                print(f"Error in update job: {e}")

        thread = threading.Thread(target=run_update, daemon=True)
        thread.start()

        return {
            "success": True,
            "message": f"Started updating up to {max_stocks} stale stocks",
            "info": "Job is running in background. Check job logs for progress."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/admin/database/stats")
async def get_database_stats():
    """
    Lấy thống kê database

    Returns:
        Thống kê về số lượng stocks, freshness, etc.
    """
    try:
        from ..database import get_db_session
        from ..services.stock_data_service import StockDataService
        from ..database.models import StockScreeningData
        from datetime import datetime, timedelta

        with get_db_session() as db:
            # Total stocks
            total_stocks = db.query(StockScreeningData).filter(
                StockScreeningData.is_active == True
            ).count()

            # Fresh stocks (< 24h)
            cutoff_24h = datetime.utcnow() - timedelta(hours=24)
            fresh_stocks = db.query(StockScreeningData).filter(
                StockScreeningData.is_active == True,
                StockScreeningData.last_updated >= cutoff_24h
            ).count()

            # Stale stocks (> 24h)
            stale_stocks = db.query(StockScreeningData).filter(
                StockScreeningData.is_active == True,
                StockScreeningData.last_updated < cutoff_24h
            ).count()

            # Never updated
            never_updated = db.query(StockScreeningData).filter(
                StockScreeningData.is_active == True,
                StockScreeningData.last_updated == None
            ).count()

            # Latest job logs
            latest_jobs = StockDataService.get_latest_job_logs(db, limit=5)
            job_logs = [
                {
                    'id': job.id,
                    'type': job.job_type,
                    'status': job.status,
                    'started_at': job.started_at.isoformat() if job.started_at else None,
                    'completed_at': job.completed_at.isoformat() if job.completed_at else None,
                    'processed': job.stocks_processed,
                    'updated': job.stocks_updated,
                    'failed': job.stocks_failed,
                    'error': job.error_message
                }
                for job in latest_jobs
            ]

        return {
            "success": True,
            "stats": {
                "total_stocks": total_stocks,
                "fresh_stocks_24h": fresh_stocks,
                "stale_stocks_24h": stale_stocks,
                "never_updated": never_updated,
                "freshness_rate": f"{(fresh_stocks / total_stocks * 100):.1f}%" if total_stocks > 0 else "0%"
            },
            "latest_jobs": job_logs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
