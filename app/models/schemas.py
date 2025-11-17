from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any
from datetime import datetime


class StockRequest(BaseModel):
    """Schema cho request lấy dữ liệu cổ phiếu"""
    symbol: str = Field(..., description="Mã cổ phiếu (VD: VNM, VCB, HPG)")
    start_date: Optional[str] = Field(None, description="Ngày bắt đầu (YYYY-MM-DD). Nếu không cung cấp sẽ lấy từ ngày niêm yết")
    end_date: Optional[str] = Field(None, description="Ngày kết thúc (YYYY-MM-DD). Nếu không cung cấp sẽ lấy đến ngày hiện tại")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "VNM",
                "start_date": "2024-01-01",
                "end_date": "2024-12-31"
            }
        }


class TechnicalIndicators(BaseModel):
    """Các chỉ số kỹ thuật"""
    SMA: Optional[Dict[str, Any]] = Field(None, description="Simple Moving Average")
    EMA: Optional[Dict[str, Any]] = Field(None, description="Exponential Moving Average")
    MACD: Optional[Dict[str, Any]] = Field(None, description="Moving Average Convergence Divergence")
    RSI: Optional[Dict[str, Any]] = Field(None, description="Relative Strength Index")
    BB: Optional[Dict[str, Any]] = Field(None, description="Bollinger Bands")
    ATR: Optional[Dict[str, Any]] = Field(None, description="Average True Range")
    OBV: Optional[Dict[str, Any]] = Field(None, description="On Balance Volume")
    Ichimoku: Optional[Dict[str, Any]] = Field(None, description="Ichimoku Cloud")
    PSAR: Optional[Dict[str, Any]] = Field(None, description="Parabolic SAR")
    MFI: Optional[Dict[str, Any]] = Field(None, description="Money Flow Index")
    AD: Optional[Dict[str, Any]] = Field(None, description="Accumulation/Distribution")
    CMF: Optional[Dict[str, Any]] = Field(None, description="Chaikin Money Flow")
    ADL: Optional[Dict[str, Any]] = Field(None, description="Advance/Decline Line")


class FundamentalIndicators(BaseModel):
    """Các chỉ số cơ bản"""
    EPS: Optional[float] = Field(None, description="Earnings Per Share")
    PE: Optional[float] = Field(None, description="Price to Earnings Ratio")
    PB: Optional[float] = Field(None, description="Price to Book Ratio")
    PS: Optional[float] = Field(None, description="Price to Sales Ratio")
    PCF: Optional[float] = Field(None, description="Price to Cash Flow Ratio")
    DY: Optional[float] = Field(None, description="Dividend Yield")
    EV_EBITDA: Optional[float] = Field(None, description="Enterprise Value to EBITDA")
    PEG: Optional[float] = Field(None, description="Price/Earnings to Growth Ratio")
    ROE: Optional[float] = Field(None, description="Return on Equity")
    ROA: Optional[float] = Field(None, description="Return on Assets")
    DE: Optional[float] = Field(None, description="Debt to Equity Ratio")
    CR: Optional[float] = Field(None, description="Current Ratio")
    NPM: Optional[float] = Field(None, description="Net Profit Margin")
    RG: Optional[float] = Field(None, description="Revenue Growth")
    OCF: Optional[float] = Field(None, description="Operating Cash Flow")
    FCF: Optional[float] = Field(None, description="Free Cash Flow")


class MacroIndicators(BaseModel):
    """Các chỉ số kinh tế vĩ mô"""
    GDP: Optional[float] = Field(None, description="Gross Domestic Product")
    CPI: Optional[float] = Field(None, description="Consumer Price Index")
    IR: Optional[float] = Field(None, description="Interest Rate")
    EXR: Optional[float] = Field(None, description="Exchange Rate")
    UR: Optional[float] = Field(None, description="Unemployment Rate")
    FGI: Optional[float] = Field(None, description="Fear and Greed Index")
    PCR: Optional[float] = Field(None, description="Put/Call Ratio")


class CompanyInfo(BaseModel):
    """Thông tin công ty"""
    symbol: Optional[str] = None
    company_name: Optional[str] = None
    exchange: Optional[str] = None
    industry: Optional[str] = None
    sector: Optional[str] = None
    listing_date: Optional[str] = None
    market_cap: Optional[float] = None
    shares_outstanding: Optional[float] = None
    website: Optional[str] = None
    description: Optional[str] = None


class StockResponse(BaseModel):
    """Schema cho response trả về dữ liệu cổ phiếu"""
    symbol: str
    company_info: Optional[CompanyInfo] = None
    price_data: Optional[List[Dict[str, Any]]] = Field(None, description="Dữ liệu giá theo thời gian")
    technical_indicators: Optional[TechnicalIndicators] = None
    fundamental_indicators: Optional[FundamentalIndicators] = None
    macro_indicators: Optional[MacroIndicators] = None
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Thông tin metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "symbol": "VNM",
                "company_info": {
                    "company_name": "Vinamilk",
                    "exchange": "HOSE",
                    "industry": "Food & Beverage"
                },
                "price_data": [
                    {
                        "date": "2024-01-01",
                        "open": 75000,
                        "high": 76000,
                        "low": 74500,
                        "close": 75500,
                        "volume": 1000000
                    }
                ],
                "technical_indicators": {},
                "fundamental_indicators": {},
                "macro_indicators": {},
                "metadata": {
                    "total_records": 250,
                    "start_date": "2024-01-01",
                    "end_date": "2024-12-31"
                }
            }
        }
