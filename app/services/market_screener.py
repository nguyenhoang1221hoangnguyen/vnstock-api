"""
Market Screener Service
Quét toàn bộ thị trường VN để tìm cơ hội đầu tư
"""
from typing import List, Dict, Any, Optional
from vnstock import Vnstock
import pandas as pd
from datetime import datetime, timedelta
import os
import random

from ..database import get_db_session
from .stock_data_service import StockDataService


class MarketScreener:
    def __init__(self):
        self.stock = Vnstock()
        self.use_mock = os.getenv('USE_MOCK_SCREENER', 'false').lower() == 'true'  # Set to false for real data
        self.cache = {}  # Simple cache to reduce API calls
        self.cache_timeout = 300  # 5 minutes
        self.use_database = True  # Use database for screening

    def get_all_symbols(self, exchange: str = "ALL") -> List[str]:
        """
        Lấy danh sách tất cả mã cổ phiếu
        exchange: HOSE, HNX, UPCOM, ALL
        """
        # Top liquid stocks (limit to reduce API calls and rate limit)
        HOSE_STOCKS = [
            # VN30 Blue chips - Most liquid stocks
            "VNM", "VIC", "VHM", "VCB", "BID", "CTG", "MBB", "TCB", "ACB",
            "HPG", "MSN", "FPT", "VPB", "PLX", "GAS", "POW", "VRE", "SSI",
            "HDB", "STB", "SAB", "MWG", "VJC", "GMD", "NVL", "PDR",
            "TPB", "SHB", "VIB", "LPB", "EIB"
        ]

        HNX_STOCKS = [
            "PVS", "CEO", "VCS", "SHS", "VND", "PVX", "IDC", "PVI", "PVT",
            "TNG", "DTD", "PLC", "NHH", "NDN", "THD", "DNP", "HUT", "DBC"
        ]

        UPCOM_STOCKS = [
            "AAV", "ACG", "ADS", "ARM", "BAB", "BST", "CSM", "DAE", "FTS"
        ]

        if exchange == "HOSE":
            return HOSE_STOCKS
        elif exchange == "HNX":
            return HNX_STOCKS
        elif exchange == "UPCOM":
            return UPCOM_STOCKS
        else:  # ALL
            return HOSE_STOCKS + HNX_STOCKS + UPCOM_STOCKS

    def screen_stocks(
        self,
        filters: Dict[str, Any],
        exchange: str = "ALL",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Quét cổ phiếu theo bộ lọc
        Nếu use_database=True, sẽ query từ database (nhanh, không rate limit)
        Nếu use_database=False, sẽ gọi API trực tiếp (chậm, có rate limit)

        filters: {
            'pe_min': 0,
            'pe_max': 15,
            'pb_max': 2,
            'roe_min': 15,
            'market_cap_min': 1000000000000,  # 1T
            'price_change_min': -10,
            'price_change_max': 50,
            'volume_min': 100000,
            'rsi_min': 0,
            'rsi_max': 30  # oversold
        }
        """
        # Use database for fast screening
        if self.use_database:
            return self._screen_from_database(filters, exchange, limit)

        # Fallback to API (slow, with rate limit)
        return self._screen_from_api(filters, exchange, limit)

    def _screen_from_database(
        self,
        filters: Dict[str, Any],
        exchange: str = "ALL",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Screen stocks từ database - Nhanh, không rate limit"""
        with get_db_session() as db:
            stocks = StockDataService.screen_stocks(
                db=db,
                filters=filters,
                exchange=exchange if exchange != "ALL" else None,
                limit=limit
            )

            # Convert to dict
            results = [stock.to_dict() for stock in stocks]
            print(f"✓ Found {len(results)} stocks from database")
            return results

    def _screen_from_api(
        self,
        filters: Dict[str, Any],
        exchange: str = "ALL",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Screen stocks từ API - Chậm, có rate limit"""
        symbols = self.get_all_symbols(exchange)
        results = []

        print(f"Screening {len(symbols)} stocks from API with filters: {filters}")

        for symbol in symbols:
            try:
                stock_data = self._get_stock_screening_data(symbol)

                if stock_data and self._matches_filters(stock_data, filters):
                    results.append(stock_data)

                    if len(results) >= limit:
                        break

            except SystemExit as e:
                # Handle rate limit from vnstock - skip this stock and continue
                print(f"Rate limit or system exit for {symbol}: {e}")
                continue
            except Exception as e:
                print(f"Error screening {symbol}: {e}")
                continue

        # Sort by score (can customize scoring logic)
        results.sort(key=lambda x: x.get('score', 0), reverse=True)

        return results[:limit]

    def _get_mock_screening_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Generate mock data for screening (for demo purposes)"""
        # Mock data với giá trị ngẫu nhiên nhưng realistic
        mock_data = {
            'symbol': symbol,
            'company_name': f"{symbol} Corporation",
            'current_price': random.uniform(10000, 150000),
            'price_change_30d': random.uniform(-20, 40),
            'volume': random.randint(50000, 5000000),
            'market_cap': random.uniform(500000000000, 50000000000000),
            'pe': random.uniform(5, 25),
            'pb': random.uniform(0.5, 4),
            'roe': random.uniform(5, 30),
            'rsi': random.uniform(20, 80),
            'eps': random.uniform(1000, 10000),
        }

        # Calculate score
        mock_data['score'] = self._calculate_screening_score(mock_data)

        return mock_data

    def _get_stock_screening_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Lấy dữ liệu cần thiết cho screening"""
        # Use mock data if enabled
        if self.use_mock:
            return self._get_mock_screening_data(symbol)

        # Check cache first
        cache_key = f"screening_{symbol}"
        if cache_key in self.cache:
            cached_data, cached_time = self.cache[cache_key]
            if (datetime.now() - cached_time).total_seconds() < self.cache_timeout:
                return cached_data

        try:
            import time
            time.sleep(2)  # Increase delay to 2 seconds to avoid rate limit
            stock = Vnstock().stock(symbol=symbol, source='VCI')

            # Get company overview
            overview = stock.company.overview()
            if overview is None or overview.empty:
                return None

            # Get financial ratios
            ratios = stock.finance.ratio(period='year', lang='en')
            if ratios is None or ratios.empty:
                return None

            # Get latest price data
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            price_data = stock.quote.history(start=start_date, end=end_date)
            if price_data is None or price_data.empty:
                return None

            # Extract data
            latest_price = price_data.iloc[-1] if not price_data.empty else None
            first_price = price_data.iloc[0] if not price_data.empty else None

            if latest_price is None or first_price is None:
                return None

            # Calculate price change
            price_change = ((latest_price['close'] - first_price['close']) / first_price['close']) * 100

            # Extract ratios
            latest_ratios = ratios.iloc[0] if not ratios.empty else {}

            # Calculate RSI (simple implementation)
            rsi = self._calculate_rsi(price_data['close'])

            # Get market cap
            market_cap = overview.get('marketCap', 0) if isinstance(overview, dict) else \
                        overview['marketCap'].iloc[0] if 'marketCap' in overview.columns else 0

            # Get PE, PB, ROE from ratios
            pe = self._extract_ratio(ratios, 'PE') or self._extract_ratio(ratios, 'P/E')
            pb = self._extract_ratio(ratios, 'PB') or self._extract_ratio(ratios, 'P/B')
            roe = self._extract_ratio(ratios, 'ROE')
            eps = self._extract_ratio(ratios, 'EPS')

            # Calculate score (higher is better)
            score = self._calculate_screening_score({
                'pe': pe,
                'pb': pb,
                'roe': roe,
                'price_change': price_change,
                'rsi': rsi
            })

            result = {
                'symbol': symbol,
                'company_name': overview.get('organName', symbol) if isinstance(overview, dict) else \
                               overview['organName'].iloc[0] if 'organName' in overview.columns else symbol,
                'current_price': float(latest_price['close']),
                'price_change_30d': float(price_change),
                'volume': int(latest_price['volume']),
                'market_cap': float(market_cap) if market_cap else 0,
                'pe': float(pe) if pe else None,
                'pb': float(pb) if pb else None,
                'roe': float(roe) if roe else None,
                'eps': float(eps) if eps else None,
                'rsi': float(rsi) if rsi else None,
                'score': score,
                'exchange': overview.get('exchange', 'N/A') if isinstance(overview, dict) else \
                           overview['exchange'].iloc[0] if 'exchange' in overview.columns else 'N/A'
            }

            # Cache the result
            self.cache[cache_key] = (result, datetime.now())

            return result

        except SystemExit as e:
            # Handle rate limit from vnstock
            print(f"Rate limit or system exit for {symbol}: {e}")
            return None
        except Exception as e:
            print(f"Error getting data for {symbol}: {e}")
            return None

    def _extract_ratio(self, ratios_df: pd.DataFrame, key: str) -> Optional[float]:
        """Extract ratio value from multi-level DataFrame"""
        try:
            if ratios_df is None or ratios_df.empty:
                return None

            # Check if it's in columns
            if key in ratios_df.columns:
                value = ratios_df[key].iloc[0]
                return float(value) if value and str(value).lower() not in ['nan', 'none', ''] else None

            # Check in multi-level columns
            for col in ratios_df.columns:
                if isinstance(col, tuple):
                    if key in col or key.upper() in str(col).upper():
                        value = ratios_df[col].iloc[0]
                        return float(value) if value and str(value).lower() not in ['nan', 'none', ''] else None
                elif key.upper() in str(col).upper():
                    value = ratios_df[col].iloc[0]
                    return float(value) if value and str(value).lower() not in ['nan', 'none', ''] else None

            return None
        except:
            return None

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> Optional[float]:
        """Calculate RSI indicator"""
        try:
            if len(prices) < period + 1:
                return None

            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            return rsi.iloc[-1] if not rsi.empty else None
        except:
            return None

    def _matches_filters(self, stock_data: Dict[str, Any], filters: Dict[str, Any]) -> bool:
        """Check if stock matches all filters"""
        try:
            # PE filter
            if 'pe_min' in filters and stock_data.get('pe'):
                if stock_data['pe'] < filters['pe_min']:
                    return False

            if 'pe_max' in filters and stock_data.get('pe'):
                if stock_data['pe'] > filters['pe_max']:
                    return False

            # PB filter
            if 'pb_max' in filters and stock_data.get('pb'):
                if stock_data['pb'] > filters['pb_max']:
                    return False

            # ROE filter
            if 'roe_min' in filters and stock_data.get('roe'):
                if stock_data['roe'] < filters['roe_min']:
                    return False

            # Market cap filter
            if 'market_cap_min' in filters:
                if stock_data.get('market_cap', 0) < filters['market_cap_min']:
                    return False

            # Price change filter
            if 'price_change_min' in filters:
                if stock_data['price_change_30d'] < filters['price_change_min']:
                    return False

            if 'price_change_max' in filters:
                if stock_data['price_change_30d'] > filters['price_change_max']:
                    return False

            # Volume filter
            if 'volume_min' in filters:
                if stock_data['volume'] < filters['volume_min']:
                    return False

            # RSI filter
            if 'rsi_min' in filters and stock_data.get('rsi'):
                if stock_data['rsi'] < filters['rsi_min']:
                    return False

            if 'rsi_max' in filters and stock_data.get('rsi'):
                if stock_data['rsi'] > filters['rsi_max']:
                    return False

            return True

        except Exception as e:
            print(f"Error in filter matching: {e}")
            return False

    def _calculate_screening_score(self, data: Dict[str, Any]) -> float:
        """
        Calculate screening score (0-100)
        Higher score = better opportunity
        """
        score = 50  # Base score

        try:
            # PE score: Lower is better (but not negative)
            if data.get('pe') and data['pe'] > 0:
                if data['pe'] < 10:
                    score += 15
                elif data['pe'] < 15:
                    score += 10
                elif data['pe'] < 20:
                    score += 5
                elif data['pe'] > 30:
                    score -= 10

            # PB score: Lower is better
            if data.get('pb'):
                if data['pb'] < 1:
                    score += 10
                elif data['pb'] < 2:
                    score += 5
                elif data['pb'] > 3:
                    score -= 5

            # ROE score: Higher is better
            if data.get('roe'):
                if data['roe'] > 20:
                    score += 15
                elif data['roe'] > 15:
                    score += 10
                elif data['roe'] > 10:
                    score += 5
                elif data['roe'] < 5:
                    score -= 10

            # Price momentum
            if data.get('price_change'):
                if 0 < data['price_change'] < 20:  # Positive but not too high
                    score += 10
                elif data['price_change'] > 50:  # Too hot
                    score -= 5
                elif data['price_change'] < -20:  # Falling too much
                    score -= 10

            # RSI score
            if data.get('rsi'):
                if 20 < data['rsi'] < 40:  # Oversold but not extreme
                    score += 15
                elif 40 < data['rsi'] < 60:  # Neutral
                    score += 5
                elif data['rsi'] > 70:  # Overbought
                    score -= 10

            return max(0, min(100, score))  # Clamp to 0-100

        except:
            return 50

    def get_preset_screens(self) -> Dict[str, Dict[str, Any]]:
        """
        Các bộ lọc preset phổ biến
        """
        return {
            "value_stocks": {
                "name": "Cổ phiếu giá trị",
                "description": "PE thấp, ROE cao, PB hợp lý",
                "filters": {
                    "pe_max": 15,
                    "pb_max": 2,
                    "roe_min": 15,
                    "market_cap_min": 1_000_000_000_000  # 1T VND
                }
            },
            "growth_stocks": {
                "name": "Cổ phiếu tăng trưởng",
                "description": "Tăng giá tốt, khối lượng cao",
                "filters": {
                    "price_change_min": 10,
                    "price_change_max": 50,
                    "volume_min": 500_000,
                    "roe_min": 10
                }
            },
            "oversold_stocks": {
                "name": "Cổ phiếu quá bán",
                "description": "RSI thấp, có thể phục hồi",
                "filters": {
                    "rsi_max": 30,
                    "pe_max": 20,
                    "roe_min": 5
                }
            },
            "dividend_stocks": {
                "name": "Cổ phiếu cổ tức",
                "description": "ROE cao, PE thấp, ổn định",
                "filters": {
                    "pe_max": 12,
                    "roe_min": 12,
                    "market_cap_min": 5_000_000_000_000  # 5T VND
                }
            },
            "breakout_stocks": {
                "name": "Cổ phiếu breakout",
                "description": "Tăng giá mạnh, khối lượng cao",
                "filters": {
                    "price_change_min": 15,
                    "volume_min": 1_000_000,
                    "rsi_min": 50,
                    "rsi_max": 70
                }
            }
        }
