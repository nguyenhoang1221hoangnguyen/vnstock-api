"""
Market Heatmap Service
Visualize toàn bộ thị trường theo sectors/industries
"""
from typing import List, Dict, Any
from vnstock import Vnstock
import pandas as pd
from datetime import datetime, timedelta
from collections import defaultdict


class MarketHeatmap:
    def __init__(self):
        self.stock = Vnstock()

    def get_market_overview(self, exchange: str = "HOSE") -> Dict[str, Any]:
        """
        Lấy tổng quan thị trường theo sectors
        """
        try:
            # Get all listings
            listing = self.stock.listing.symbols_by_exchange(exchange)

            if listing is None or listing.empty:
                return self._get_fallback_data(exchange)

            symbols = listing['ticker'].tolist()[:100]  # Limit for performance

            # Group by sector/industry
            sectors_data = defaultdict(lambda: {
                'stocks': [],
                'total_market_cap': 0,
                'avg_change': 0,
                'total_volume': 0
            })

            for symbol in symbols:
                try:
                    stock_data = self._get_stock_heatmap_data(symbol)

                    if stock_data:
                        sector = stock_data.get('sector', 'Others')
                        sectors_data[sector]['stocks'].append(stock_data)
                        sectors_data[sector]['total_market_cap'] += stock_data.get('market_cap', 0)
                        sectors_data[sector]['total_volume'] += stock_data.get('volume', 0)

                except Exception as e:
                    print(f"Error processing {symbol}: {e}")
                    continue

            # Calculate averages
            heatmap_data = []
            for sector, data in sectors_data.items():
                if data['stocks']:
                    avg_change = sum(s['price_change'] for s in data['stocks']) / len(data['stocks'])

                    heatmap_data.append({
                        'sector': sector,
                        'stocks': data['stocks'],
                        'stock_count': len(data['stocks']),
                        'total_market_cap': data['total_market_cap'],
                        'avg_price_change': avg_change,
                        'total_volume': data['total_volume']
                    })

            # Sort by market cap
            heatmap_data.sort(key=lambda x: x['total_market_cap'], reverse=True)

            return {
                'exchange': exchange,
                'timestamp': datetime.now().isoformat(),
                'sectors': heatmap_data,
                'total_stocks': sum(s['stock_count'] for s in heatmap_data),
                'market_sentiment': self._calculate_market_sentiment(heatmap_data)
            }

        except Exception as e:
            print(f"Error in get_market_overview: {e}")
            return self._get_fallback_data(exchange)

    def _get_stock_heatmap_data(self, symbol: str) -> Dict[str, Any]:
        """Lấy dữ liệu cho 1 mã cổ phiếu"""
        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')

            # Get company info
            overview = stock.company.overview()
            if overview is None or overview.empty:
                return None

            # Get price data (last 5 days)
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

            price_data = stock.quote.history(start=start_date, end=end_date)
            if price_data is None or price_data.empty:
                return None

            latest_price = price_data.iloc[-1]
            first_price = price_data.iloc[0]

            # Calculate change
            price_change = ((latest_price['close'] - first_price['close']) / first_price['close']) * 100

            # Extract sector/industry
            sector = 'Others'
            industry = 'Others'

            if isinstance(overview, dict):
                sector = overview.get('icbName3', overview.get('industry', 'Others'))
                industry = overview.get('icbName4', overview.get('sector', 'Others'))
            elif isinstance(overview, pd.DataFrame) and not overview.empty:
                if 'icbName3' in overview.columns:
                    sector = overview['icbName3'].iloc[0]
                elif 'industry' in overview.columns:
                    sector = overview['industry'].iloc[0]

                if 'icbName4' in overview.columns:
                    industry = overview['icbName4'].iloc[0]

            market_cap = 0
            if isinstance(overview, dict):
                market_cap = overview.get('marketCap', 0)
            elif 'marketCap' in overview.columns:
                market_cap = overview['marketCap'].iloc[0]

            return {
                'symbol': symbol,
                'company_name': self._extract_company_name(overview),
                'price': float(latest_price['close']),
                'price_change': float(price_change),
                'volume': int(latest_price['volume']),
                'market_cap': float(market_cap) if market_cap else 0,
                'sector': str(sector) if sector else 'Others',
                'industry': str(industry) if industry else 'Others'
            }

        except Exception as e:
            print(f"Error getting heatmap data for {symbol}: {e}")
            return None

    def _extract_company_name(self, overview) -> str:
        """Extract company name from overview data"""
        try:
            if isinstance(overview, dict):
                return overview.get('organName', overview.get('companyName', 'N/A'))
            elif isinstance(overview, pd.DataFrame) and not overview.empty:
                if 'organName' in overview.columns:
                    return overview['organName'].iloc[0]
                elif 'companyName' in overview.columns:
                    return overview['companyName'].iloc[0]
            return 'N/A'
        except:
            return 'N/A'

    def _calculate_market_sentiment(self, sectors: List[Dict]) -> str:
        """
        Calculate overall market sentiment
        Returns: BULLISH, BEARISH, NEUTRAL
        """
        try:
            if not sectors:
                return "NEUTRAL"

            # Weight by market cap
            total_weighted_change = sum(
                s['avg_price_change'] * s['total_market_cap']
                for s in sectors
            )
            total_market_cap = sum(s['total_market_cap'] for s in sectors)

            if total_market_cap == 0:
                return "NEUTRAL"

            weighted_avg_change = total_weighted_change / total_market_cap

            if weighted_avg_change > 0.5:
                return "BULLISH"
            elif weighted_avg_change < -0.5:
                return "BEARISH"
            else:
                return "NEUTRAL"

        except:
            return "NEUTRAL"

    def _get_fallback_data(self, exchange: str) -> Dict[str, Any]:
        """Fallback data when API fails"""
        return {
            'exchange': exchange,
            'timestamp': datetime.now().isoformat(),
            'sectors': [
                {
                    'sector': 'Ngân hàng',
                    'stocks': [
                        {'symbol': 'VCB', 'price': 95000, 'price_change': 1.2, 'volume': 2500000, 'market_cap': 400000000000000},
                        {'symbol': 'TCB', 'price': 24500, 'price_change': -0.5, 'volume': 8500000, 'market_cap': 80000000000000},
                        {'symbol': 'MBB', 'price': 23800, 'price_change': 0.8, 'volume': 5200000, 'market_cap': 75000000000000},
                    ],
                    'stock_count': 3,
                    'total_market_cap': 555000000000000,
                    'avg_price_change': 0.5,
                    'total_volume': 16200000
                },
                {
                    'sector': 'Bất động sản',
                    'stocks': [
                        {'symbol': 'VHM', 'price': 42500, 'price_change': -1.5, 'volume': 3200000, 'market_cap': 180000000000000},
                        {'symbol': 'VIC', 'price': 38900, 'price_change': -0.8, 'volume': 4500000, 'market_cap': 200000000000000},
                        {'symbol': 'NVL', 'price': 12300, 'price_change': 2.1, 'volume': 7800000, 'market_cap': 45000000000000},
                    ],
                    'stock_count': 3,
                    'total_market_cap': 425000000000000,
                    'avg_price_change': -0.07,
                    'total_volume': 15500000
                },
                {
                    'sector': 'Thực phẩm',
                    'stocks': [
                        {'symbol': 'VNM', 'price': 57600, 'price_change': 0.3, 'volume': 1200000, 'market_cap': 120000000000000},
                        {'symbol': 'SAB', 'price': 156000, 'price_change': 1.8, 'volume': 450000, 'market_cap': 95000000000000},
                    ],
                    'stock_count': 2,
                    'total_market_cap': 215000000000000,
                    'avg_price_change': 1.05,
                    'total_volume': 1650000
                }
            ],
            'total_stocks': 8,
            'market_sentiment': 'NEUTRAL'
        }

    def get_industry_heatmap(self, sector: str, exchange: str = "HOSE") -> Dict[str, Any]:
        """
        Get detailed heatmap for specific sector
        """
        try:
            market_data = self.get_market_overview(exchange)

            # Find sector data
            sector_data = next(
                (s for s in market_data['sectors'] if s['sector'] == sector),
                None
            )

            if not sector_data:
                return {'error': 'Sector not found'}

            # Group by industry
            industries = defaultdict(lambda: {
                'stocks': [],
                'total_market_cap': 0,
                'avg_change': 0
            })

            for stock in sector_data['stocks']:
                industry = stock.get('industry', 'Others')
                industries[industry]['stocks'].append(stock)
                industries[industry]['total_market_cap'] += stock.get('market_cap', 0)

            # Format response
            industry_data = []
            for industry, data in industries.items():
                avg_change = sum(s['price_change'] for s in data['stocks']) / len(data['stocks'])

                industry_data.append({
                    'industry': industry,
                    'stocks': data['stocks'],
                    'stock_count': len(data['stocks']),
                    'total_market_cap': data['total_market_cap'],
                    'avg_price_change': avg_change
                })

            industry_data.sort(key=lambda x: x['total_market_cap'], reverse=True)

            return {
                'sector': sector,
                'exchange': exchange,
                'industries': industry_data,
                'total_stocks': sum(i['stock_count'] for i in industry_data)
            }

        except Exception as e:
            print(f"Error in get_industry_heatmap: {e}")
            return {'error': str(e)}
