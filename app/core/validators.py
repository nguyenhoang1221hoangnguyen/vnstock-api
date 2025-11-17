"""
Input validation utilities
"""
import re
from typing import Optional, List
from datetime import datetime
from fastapi import HTTPException, status


class StockSymbolValidator:
    """Validate Vietnamese stock symbols"""

    # Vietnamese stock symbols: 3 uppercase letters
    SYMBOL_PATTERN = re.compile(r'^[A-Z]{3}$')

    # Known exchanges
    VALID_EXCHANGES = {'HOSE', 'HNX', 'UPCOM', 'ALL'}

    # Common symbols for quick validation (can be extended)
    KNOWN_SYMBOLS = {
        'VNM', 'VIC', 'VHM', 'VCB', 'BID', 'CTG', 'MBB', 'TCB', 'ACB', 'HPG',
        'VPB', 'MSN', 'FPT', 'VRE', 'GAS', 'PLX', 'SAB', 'MWG', 'HDB', 'SSI',
        'POW', 'GEX', 'NVL', 'VJC', 'PNJ', 'REE', 'DPM', 'VNX', 'DHG', 'KDH'
    }

    @classmethod
    def validate_symbol(cls, symbol: str, strict: bool = False) -> str:
        """
        Validate stock symbol

        Args:
            symbol: Stock symbol to validate
            strict: If True, check against known symbols list

        Returns:
            Uppercase validated symbol

        Raises:
            HTTPException if invalid
        """
        if not symbol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Stock symbol is required"
            )

        # Convert to uppercase
        symbol = symbol.strip().upper()

        # Check pattern
        if not cls.SYMBOL_PATTERN.match(symbol):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid stock symbol format: '{symbol}'. "
                       f"Expected 3 uppercase letters (e.g., VNM, VCB, HPG)"
            )

        # Strict mode: check against known symbols
        if strict and symbol not in cls.KNOWN_SYMBOLS:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Stock symbol '{symbol}' not found in known symbols list"
            )

        return symbol

    @classmethod
    def validate_exchange(cls, exchange: str) -> str:
        """Validate exchange name"""
        if not exchange:
            return "ALL"

        exchange = exchange.strip().upper()

        if exchange not in cls.VALID_EXCHANGES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid exchange: '{exchange}'. "
                       f"Valid exchanges: {', '.join(cls.VALID_EXCHANGES)}"
            )

        return exchange


class DateValidator:
    """Validate date inputs"""

    DATE_FORMAT = '%Y-%m-%d'
    DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    @classmethod
    def validate_date(cls, date_str: Optional[str], field_name: str = "date") -> Optional[str]:
        """
        Validate date string

        Args:
            date_str: Date string in YYYY-MM-DD format
            field_name: Name of the field for error messages

        Returns:
            Validated date string or None

        Raises:
            HTTPException if invalid
        """
        if not date_str:
            return None

        date_str = date_str.strip()

        # Check pattern
        if not cls.DATE_PATTERN.match(date_str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name} format: '{date_str}'. "
                       f"Expected YYYY-MM-DD (e.g., 2024-01-31)"
            )

        # Parse date
        try:
            date_obj = datetime.strptime(date_str, cls.DATE_FORMAT)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name}: '{date_str}'. {str(e)}"
            )

        # Check if date is not in the future
        if date_obj > datetime.now():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} cannot be in the future: '{date_str}'"
            )

        # Check if date is not too old (e.g., before 1990)
        if date_obj.year < 1990:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{field_name} cannot be before 1990: '{date_str}'"
            )

        return date_str

    @classmethod
    def validate_date_range(
        cls,
        start_date: Optional[str],
        end_date: Optional[str]
    ) -> tuple[Optional[str], Optional[str]]:
        """
        Validate date range

        Returns:
            Tuple of (start_date, end_date)

        Raises:
            HTTPException if invalid
        """
        start = cls.validate_date(start_date, "start_date")
        end = cls.validate_date(end_date, "end_date")

        # Check if start is before end
        if start and end:
            start_obj = datetime.strptime(start, cls.DATE_FORMAT)
            end_obj = datetime.strptime(end, cls.DATE_FORMAT)

            if start_obj > end_obj:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"start_date ({start}) must be before end_date ({end})"
                )

            # Check if range is too large (e.g., > 10 years)
            days_diff = (end_obj - start_obj).days
            if days_diff > 3650:  # 10 years
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Date range too large: {days_diff} days. Maximum 10 years (3650 days)"
                )

        return start, end


class IntradayValidator:
    """Validate intraday parameters"""

    VALID_INTERVALS = {'1m', '5m', '15m', '30m', '1h', '3h', '6h', '1d'}

    @classmethod
    def validate_interval(cls, interval: str) -> str:
        """Validate intraday interval"""
        if not interval:
            return '5m'

        interval = interval.strip().lower()

        if interval not in cls.VALID_INTERVALS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid interval: '{interval}'. "
                       f"Valid intervals: {', '.join(sorted(cls.VALID_INTERVALS))}"
            )

        return interval

    @classmethod
    def validate_limit(cls, limit: int, max_limit: int = 10000) -> int:
        """Validate data limit"""
        if limit < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Limit must be >= 1, got {limit}"
            )

        if limit > max_limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Limit too large: {limit}. Maximum {max_limit}"
            )

        return limit


class ScreenerValidator:
    """Validate market screener parameters"""

    @classmethod
    def validate_filters(cls, filters: dict) -> dict:
        """
        Validate screener filters

        Checks:
        - Value ranges are reasonable
        - Min is less than max
        - No negative values where inappropriate
        """
        validated = {}

        # PE ratio
        if 'pe_min' in filters:
            pe_min = filters['pe_min']
            if pe_min is not None:
                if pe_min < 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="pe_min cannot be negative"
                    )
                if pe_min > 1000:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="pe_min too large (max 1000)"
                    )
                validated['pe_min'] = pe_min

        if 'pe_max' in filters:
            pe_max = filters['pe_max']
            if pe_max is not None:
                if pe_max < 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="pe_max cannot be negative"
                    )
                if pe_max > 1000:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="pe_max too large (max 1000)"
                    )
                validated['pe_max'] = pe_max

        # Check min < max
        if 'pe_min' in validated and 'pe_max' in validated:
            if validated['pe_min'] > validated['pe_max']:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"pe_min ({validated['pe_min']}) must be <= pe_max ({validated['pe_max']})"
                )

        # ROE (percentage)
        if 'roe_min' in filters:
            roe_min = filters['roe_min']
            if roe_min is not None:
                if roe_min < -100 or roe_min > 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="roe_min must be between -100 and 200"
                    )
                validated['roe_min'] = roe_min

        if 'roe_max' in filters:
            roe_max = filters['roe_max']
            if roe_max is not None:
                if roe_max < -100 or roe_max > 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="roe_max must be between -100 and 200"
                    )
                validated['roe_max'] = roe_max

        # Market cap (in VND)
        if 'market_cap_min' in filters:
            mc_min = filters['market_cap_min']
            if mc_min is not None:
                if mc_min < 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="market_cap_min cannot be negative"
                    )
                validated['market_cap_min'] = mc_min

        # Volume
        if 'volume_min' in filters:
            vol_min = filters['volume_min']
            if vol_min is not None:
                if vol_min < 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="volume_min cannot be negative"
                    )
                validated['volume_min'] = vol_min

        # Copy other filters
        for key in ['pb_min', 'pb_max', 'rsi_min', 'rsi_max',
                    'price_change_min', 'price_change_max']:
            if key in filters and filters[key] is not None:
                validated[key] = filters[key]

        return validated


class PaginationValidator:
    """Validate pagination parameters"""

    @classmethod
    def validate_pagination(
        cls,
        limit: int = 50,
        offset: int = 0,
        max_limit: int = 200
    ) -> tuple[int, int]:
        """
        Validate pagination parameters

        Returns:
            Tuple of (limit, offset)
        """
        if limit < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Limit must be >= 1, got {limit}"
            )

        if limit > max_limit:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Limit too large: {limit}. Maximum {max_limit}"
            )

        if offset < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Offset must be >= 0, got {offset}"
            )

        return limit, offset
