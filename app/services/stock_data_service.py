"""
Service for managing stock screening data in database
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from ..database.models import StockScreeningData, ScreeningJobLog


class StockDataService:
    """Service để quản lý stock data trong database"""

    @staticmethod
    def get_stock_data(db: Session, symbol: str) -> Optional[StockScreeningData]:
        """Lấy dữ liệu của một cổ phiếu"""
        return db.query(StockScreeningData).filter(
            StockScreeningData.symbol == symbol.upper()
        ).first()

    @staticmethod
    def get_all_stocks(db: Session, exchange: Optional[str] = None) -> List[StockScreeningData]:
        """Lấy tất cả cổ phiếu"""
        query = db.query(StockScreeningData).filter(StockScreeningData.is_active == True)
        if exchange:
            query = query.filter(StockScreeningData.exchange == exchange.upper())
        return query.all()

    @staticmethod
    def upsert_stock_data(db: Session, stock_data: Dict) -> StockScreeningData:
        """
        Insert or update stock data
        Nếu symbol đã tồn tại thì update, nếu chưa thì insert
        """
        symbol = stock_data.get('symbol', '').upper()
        existing = db.query(StockScreeningData).filter(
            StockScreeningData.symbol == symbol
        ).first()

        if existing:
            # Update existing record
            for key, value in stock_data.items():
                if hasattr(existing, key) and key != 'id':
                    setattr(existing, key, value)
            existing.last_updated = datetime.utcnow()
            db.commit()
            db.refresh(existing)
            return existing
        else:
            # Insert new record
            new_stock = StockScreeningData(**stock_data)
            new_stock.last_updated = datetime.utcnow()
            db.add(new_stock)
            db.commit()
            db.refresh(new_stock)
            return new_stock

    @staticmethod
    def is_data_fresh(db: Session, symbol: str, max_age_hours: int = 24) -> bool:
        """
        Kiểm tra xem dữ liệu có còn mới không
        max_age_hours: số giờ tối đa dữ liệu được coi là fresh
        """
        stock = db.query(StockScreeningData).filter(
            StockScreeningData.symbol == symbol.upper()
        ).first()

        if not stock or not stock.last_updated:
            return False

        age = datetime.utcnow() - stock.last_updated
        return age < timedelta(hours=max_age_hours)

    @staticmethod
    def get_stale_stocks(db: Session, max_age_hours: int = 24, limit: Optional[int] = None) -> List[StockScreeningData]:
        """Lấy danh sách cổ phiếu có data cũ cần update"""
        cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
        query = db.query(StockScreeningData).filter(
            or_(
                StockScreeningData.last_updated < cutoff_time,
                StockScreeningData.last_updated == None
            ),
            StockScreeningData.is_active == True
        ).order_by(StockScreeningData.last_updated.asc())

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def screen_stocks(
        db: Session,
        filters: Dict,
        exchange: Optional[str] = None,
        limit: int = 50
    ) -> List[StockScreeningData]:
        """
        Screen stocks based on filters từ database
        """
        query = db.query(StockScreeningData).filter(StockScreeningData.is_active == True)

        # Apply exchange filter
        if exchange:
            query = query.filter(StockScreeningData.exchange == exchange.upper())

        # Apply dynamic filters
        if 'pe_min' in filters and filters['pe_min'] is not None:
            query = query.filter(StockScreeningData.pe >= filters['pe_min'])
        if 'pe_max' in filters and filters['pe_max'] is not None:
            query = query.filter(StockScreeningData.pe <= filters['pe_max'])

        if 'pb_min' in filters and filters['pb_min'] is not None:
            query = query.filter(StockScreeningData.pb >= filters['pb_min'])
        if 'pb_max' in filters and filters['pb_max'] is not None:
            query = query.filter(StockScreeningData.pb <= filters['pb_max'])

        if 'roe_min' in filters and filters['roe_min'] is not None:
            query = query.filter(StockScreeningData.roe >= filters['roe_min'])
        if 'roe_max' in filters and filters['roe_max'] is not None:
            query = query.filter(StockScreeningData.roe <= filters['roe_max'])

        if 'price_change_min' in filters and filters['price_change_min'] is not None:
            query = query.filter(StockScreeningData.price_change_30d >= filters['price_change_min'])
        if 'price_change_max' in filters and filters['price_change_max'] is not None:
            query = query.filter(StockScreeningData.price_change_30d <= filters['price_change_max'])

        if 'volume_min' in filters and filters['volume_min'] is not None:
            query = query.filter(StockScreeningData.volume >= filters['volume_min'])

        if 'market_cap_min' in filters and filters['market_cap_min'] is not None:
            query = query.filter(StockScreeningData.market_cap >= filters['market_cap_min'])

        if 'rsi_min' in filters and filters['rsi_min'] is not None:
            query = query.filter(StockScreeningData.rsi >= filters['rsi_min'])
        if 'rsi_max' in filters and filters['rsi_max'] is not None:
            query = query.filter(StockScreeningData.rsi <= filters['rsi_max'])

        # Order by score descending
        query = query.order_by(StockScreeningData.score.desc())

        # Limit results
        query = query.limit(limit)

        return query.all()

    @staticmethod
    def create_job_log(
        db: Session,
        job_type: str,
        status: str = 'running'
    ) -> ScreeningJobLog:
        """Tạo log cho background job"""
        log = ScreeningJobLog(
            job_type=job_type,
            status=status,
            started_at=datetime.utcnow()
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        return log

    @staticmethod
    def update_job_log(
        db: Session,
        job_id: int,
        status: str,
        stocks_processed: int = 0,
        stocks_updated: int = 0,
        stocks_failed: int = 0,
        error_message: Optional[str] = None
    ):
        """Cập nhật log của job"""
        log = db.query(ScreeningJobLog).filter(ScreeningJobLog.id == job_id).first()
        if log:
            log.status = status
            log.stocks_processed = stocks_processed
            log.stocks_updated = stocks_updated
            log.stocks_failed = stocks_failed
            if error_message:
                log.error_message = error_message
            if status in ['completed', 'failed']:
                log.completed_at = datetime.utcnow()
            db.commit()

    @staticmethod
    def get_latest_job_logs(db: Session, limit: int = 10) -> List[ScreeningJobLog]:
        """Lấy các job log gần nhất"""
        return db.query(ScreeningJobLog).order_by(
            ScreeningJobLog.started_at.desc()
        ).limit(limit).all()
