"""
Intraday data service for processing tick data into candlesticks
"""
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from vnstock import Vnstock


class IntradayService:
    """Service for fetching and processing intraday stock data"""

    # Mapping of interval to minutes
    INTERVAL_MINUTES = {
        '1m': 1,
        '5m': 5,
        '15m': 15,
        '30m': 30,
        '1h': 60,
        '3h': 180,
        '6h': 360,
        '1d': 1440,  # Daily data fallback
    }

    def __init__(self, source: str = 'VCI'):
        """
        Initialize intraday service

        Args:
            source: Data source (VCI, TCBS, MSN)
        """
        self.source = source
        self.stock_api = Vnstock()

    def get_intraday_candles(
        self,
        symbol: str,
        interval: str = '5m',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 5000
    ) -> List[Dict]:
        """
        Get intraday candlestick data for a symbol

        Args:
            symbol: Stock symbol
            interval: Time interval (1m, 5m, 15m, 30m, 1h, 3h, 6h)
            start_date: Start date (YYYY-MM-DD) - optional
            end_date: End date (YYYY-MM-DD) - optional
            limit: Maximum number of ticks to fetch

        Returns:
            List of candlestick dictionaries with OHLCV data
        """
        if interval not in self.INTERVAL_MINUTES:
            raise ValueError(f"Invalid interval. Supported: {list(self.INTERVAL_MINUTES.keys())}")

        # For daily data, use the regular history method
        if interval == '1d':
            return self._get_daily_data(symbol, start_date, end_date)

        # Get tick data
        stock = self.stock_api.stock(symbol=symbol, source=self.source)
        tick_data = stock.quote.intraday(symbol=symbol, page_size=limit, show_log=False)

        if tick_data is None or len(tick_data) == 0:
            return []

        # Filter by date range if provided
        if start_date or end_date:
            tick_data = self._filter_by_date_range(tick_data, start_date, end_date)

        # Convert ticks to candlesticks
        candles = self._aggregate_ticks_to_candles(tick_data, interval)

        return candles

    def _get_daily_data(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict]:
        """Get daily candlestick data"""
        stock = self.stock_api.stock(symbol=symbol, source=self.source)

        # Default to last 30 days if no dates provided
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        df = stock.quote.history(start=start_date, end=end_date, interval='1D')

        if df is None or len(df) == 0:
            return []

        # Convert to standard format
        candles = []
        for _, row in df.iterrows():
            candles.append({
                'time': row['time'].isoformat() if hasattr(row['time'], 'isoformat') else str(row['time']),
                'open': float(row['open']),
                'high': float(row['high']),
                'low': float(row['low']),
                'close': float(row['close']),
                'volume': int(row['volume'])
            })

        return candles

    def _filter_by_date_range(
        self,
        df: pd.DataFrame,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Filter dataframe by date range"""
        if 'time' not in df.columns:
            return df

        # Ensure time column is datetime
        if not pd.api.types.is_datetime64_any_dtype(df['time']):
            df['time'] = pd.to_datetime(df['time'])

        if start_date:
            start_dt = pd.to_datetime(start_date)
            # If df['time'] has timezone, localize start_dt to the same timezone
            if df['time'].dt.tz is not None:
                start_dt = start_dt.tz_localize(df['time'].dt.tz)
            df = df[df['time'] >= start_dt]

        if end_date:
            end_dt = pd.to_datetime(end_date) + timedelta(days=1)  # Include end date
            # If df['time'] has timezone, localize end_dt to the same timezone
            if df['time'].dt.tz is not None:
                end_dt = end_dt.tz_localize(df['time'].dt.tz)
            df = df[df['time'] < end_dt]

        return df

    def _aggregate_ticks_to_candles(
        self,
        tick_data: pd.DataFrame,
        interval: str
    ) -> List[Dict]:
        """
        Aggregate tick data into candlesticks

        Args:
            tick_data: DataFrame with columns: time, price, volume
            interval: Time interval (1m, 5m, 15m, etc.)

        Returns:
            List of candlestick dictionaries
        """
        if tick_data is None or len(tick_data) == 0:
            return []

        # Ensure time column is datetime
        if not pd.api.types.is_datetime64_any_dtype(tick_data['time']):
            tick_data['time'] = pd.to_datetime(tick_data['time'])

        # Sort by time ascending
        tick_data = tick_data.sort_values('time')

        # Get interval in minutes
        interval_minutes = self.INTERVAL_MINUTES[interval]

        # Resample to the specified interval
        tick_data.set_index('time', inplace=True)

        # Aggregate OHLCV data
        resampled = tick_data.resample(f'{interval_minutes}min').agg({
            'price': ['first', 'max', 'min', 'last'],
            'volume': 'sum'
        })

        # Remove rows with no data
        resampled = resampled.dropna()

        # Convert to list of dictionaries
        candles = []
        for timestamp, row in resampled.iterrows():
            # Skip if all values are NaN
            if pd.isna(row[('price', 'first')]):
                continue

            candles.append({
                'time': timestamp.isoformat(),
                'open': float(row[('price', 'first')]),
                'high': float(row[('price', 'max')]),
                'low': float(row[('price', 'min')]),
                'close': float(row[('price', 'last')]),
                'volume': int(row[('volume', 'sum')]) if not pd.isna(row[('volume', 'sum')]) else 0
            })

        return candles

    def get_supported_intervals(self) -> List[str]:
        """Get list of supported time intervals"""
        return list(self.INTERVAL_MINUTES.keys())
