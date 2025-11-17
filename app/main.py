"""
Main FastAPI application
"""
# Patch vnai ngay từ đầu
from .core import vnstock_patch

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router

# Tạo FastAPI app
app = FastAPI(
    title="VNStock API",
    description="""
    API để lấy dữ liệu chứng khoán thị trường Việt Nam và tính toán các chỉ số phân tích.

    ## Tính năng

    * **Dữ liệu giá**: Lấy dữ liệu giá lịch sử từ ngày niêm yết hoặc trong khoảng thời gian tùy chọn
    * **Thông tin công ty**: Thông tin chi tiết về công ty niêm yết
    * **Chỉ số kỹ thuật**: SMA, EMA, MACD, RSI, Bollinger Bands, ATR, OBV, Ichimoku, PSAR, MFI, A/D, CMF, ADL
    * **Chỉ số cơ bản**: EPS, P/E, P/B, P/S, P/CF, DY, EV/EBITDA, PEG, ROE, ROA, D/E, CR, NPM, RG, OCF, FCF
    * **Chỉ số vĩ mô**: GDP, CPI, IR, EXR, UR, FGI, PCR

    ## Sử dụng với n8n

    API này được thiết kế để tích hợp dễ dàng với n8n và các hệ thống automation khác.
    Dữ liệu trả về dưới dạng JSON cấu trúc, sẵn sàng cho AI agent phân tích.
    """,
    version="1.0.0",
    contact={
        "name": "VNStock API Support",
        "url": "https://github.com/vnstock",
    },
    license_info={
        "name": "MIT",
    }
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Trong production nên giới hạn origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router
app.include_router(router)

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Chạy khi application khởi động
    """
    print("Starting VNStock API...")
    print("Documentation available at: http://localhost:8000/docs")

    # Initialize database
    from .database import init_db
    init_db()
    print("✓ Database initialized")

    # Initialize background scheduler
    from .scheduler import init_scheduler
    init_scheduler()

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Chạy khi application tắt
    """
    print("Shutting down VNStock API...")

    # Stop scheduler
    from .scheduler import stop_scheduler
    stop_scheduler()

    # Close database
    from .database import close_db
    close_db()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
