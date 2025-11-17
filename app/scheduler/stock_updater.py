"""
Background job để tự động cập nhật dữ liệu cổ phiếu
"""
import time
from datetime import datetime
from typing import List
from vnstock import Vnstock

from ..database import get_db_session
from ..services.stock_data_service import StockDataService
from ..services.market_screener import MarketScreener


class StockDataUpdater:
    """Background worker để update stock data"""

    def __init__(self):
        self.screener = MarketScreener()

    def update_single_stock(self, symbol: str) -> bool:
        """
        Cập nhật dữ liệu cho 1 cổ phiếu
        Return True nếu thành công, False nếu thất bại
        """
        try:
            # Lấy dữ liệu từ API
            stock_data = self.screener._get_stock_screening_data(symbol)

            if not stock_data:
                print(f"No data returned for {symbol}")
                return False

            # Lưu vào database
            with get_db_session() as db:
                StockDataService.upsert_stock_data(db, stock_data)

            print(f"✓ Updated {symbol}")
            return True

        except SystemExit as e:
            print(f"✗ Rate limit for {symbol}: {e}")
            return False
        except Exception as e:
            print(f"✗ Error updating {symbol}: {e}")
            return False

    def update_stale_stocks(self, max_stocks: int = 50, delay_seconds: int = 3):
        """
        Cập nhật các cổ phiếu có dữ liệu cũ
        """
        with get_db_session() as db:
            # Tạo job log
            job_log = StockDataService.create_job_log(db, job_type='update_stale')

            try:
                # Lấy danh sách cổ phiếu cần update
                stale_stocks = StockDataService.get_stale_stocks(
                    db, max_age_hours=24, limit=max_stocks
                )

                print(f"Found {len(stale_stocks)} stale stocks to update")

                processed = 0
                updated = 0
                failed = 0

                for stock in stale_stocks:
                    symbol = stock.symbol

                    # Update stock
                    success = self.update_single_stock(symbol)

                    processed += 1
                    if success:
                        updated += 1
                    else:
                        failed += 1

                    # Delay để tránh rate limit
                    if processed < len(stale_stocks):
                        time.sleep(delay_seconds)

                # Update job log
                StockDataService.update_job_log(
                    db,
                    job_id=job_log.id,
                    status='completed',
                    stocks_processed=processed,
                    stocks_updated=updated,
                    stocks_failed=failed
                )

                print(f"Job completed: {processed} processed, {updated} updated, {failed} failed")

            except Exception as e:
                # Update job log with error
                StockDataService.update_job_log(
                    db,
                    job_id=job_log.id,
                    status='failed',
                    error_message=str(e)
                )
                print(f"Job failed: {e}")
                raise

    def scan_all_symbols(self, exchange: str = 'HOSE', delay_seconds: int = 3):
        """
        Scan tất cả symbols từ một sàn
        Dùng cho lần đầu tiên populate database
        """
        with get_db_session() as db:
            # Tạo job log
            job_log = StockDataService.create_job_log(db, job_type='full_scan')

            try:
                # Lấy tất cả symbols
                symbols = self.screener.get_all_symbols(exchange)
                print(f"Found {len(symbols)} symbols on {exchange}")

                processed = 0
                updated = 0
                failed = 0

                for symbol in symbols:
                    # Update stock
                    success = self.update_single_stock(symbol)

                    processed += 1
                    if success:
                        updated += 1
                    else:
                        failed += 1

                    # Delay để tránh rate limit
                    if processed < len(symbols):
                        time.sleep(delay_seconds)

                    # Log progress every 10 stocks
                    if processed % 10 == 0:
                        print(f"Progress: {processed}/{len(symbols)} stocks")

                # Update job log
                StockDataService.update_job_log(
                    db,
                    job_id=job_log.id,
                    status='completed',
                    stocks_processed=processed,
                    stocks_updated=updated,
                    stocks_failed=failed
                )

                print(f"Full scan completed: {processed} processed, {updated} updated, {failed} failed")

            except Exception as e:
                # Update job log with error
                StockDataService.update_job_log(
                    db,
                    job_id=job_log.id,
                    status='failed',
                    error_message=str(e)
                )
                print(f"Full scan failed: {e}")
                raise


# Global updater instance
stock_updater = StockDataUpdater()


def run_daily_update():
    """Job chạy hàng ngày để update dữ liệu"""
    print(f"[{datetime.now()}] Running daily stock update...")
    try:
        stock_updater.update_stale_stocks(max_stocks=100, delay_seconds=2)
        print(f"[{datetime.now()}] Daily update completed")
    except Exception as e:
        print(f"[{datetime.now()}] Daily update failed: {e}")


def run_hourly_update():
    """Job chạy hàng giờ để update một số cổ phiếu"""
    print(f"[{datetime.now()}] Running hourly stock update...")
    try:
        stock_updater.update_stale_stocks(max_stocks=20, delay_seconds=3)
        print(f"[{datetime.now()}] Hourly update completed")
    except Exception as e:
        print(f"[{datetime.now()}] Hourly update failed: {e}")
