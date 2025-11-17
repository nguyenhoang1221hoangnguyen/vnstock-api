"""
Database models for stock screening data
"""
from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class StockScreeningData(Base):
    """Model để lưu trữ dữ liệu screening của cổ phiếu"""
    __tablename__ = "stock_screening_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), unique=True, index=True, nullable=False)
    exchange = Column(String(10), index=True)

    # Company info
    company_name = Column(String(255))
    industry = Column(String(100))
    sector = Column(String(100))

    # Price data
    current_price = Column(Float)
    price_change_30d = Column(Float)  # % change in 30 days
    volume = Column(Float)

    # Financial ratios
    pe = Column(Float)  # P/E ratio
    pb = Column(Float)  # P/B ratio
    roe = Column(Float)  # Return on Equity
    eps = Column(Float)  # Earnings per Share
    market_cap = Column(Float)

    # Technical indicators
    rsi = Column(Float)  # RSI 14

    # Metadata
    score = Column(Float, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Indexes for faster queries
    __table_args__ = (
        Index('idx_exchange_score', 'exchange', 'score'),
        Index('idx_pe_roe', 'pe', 'roe'),
        Index('idx_last_updated', 'last_updated'),
    )

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'symbol': self.symbol,
            'exchange': self.exchange,
            'company_name': self.company_name,
            'industry': self.industry,
            'sector': self.sector,
            'price': self.current_price,  # For backward compatibility
            'current_price': self.current_price,
            'price_change': self.price_change_30d,
            'price_change_30d': self.price_change_30d,
            'volume': self.volume,
            'pe': self.pe,
            'pb': self.pb,
            'roe': self.roe,
            'eps': self.eps,
            'market_cap': self.market_cap,
            'rsi': self.rsi,
            'score': self.score,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }


class ScreeningJobLog(Base):
    """Model để log các lần chạy background job"""
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
