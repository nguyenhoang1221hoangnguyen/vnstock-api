"""
Service để lấy dữ liệu từ vnstock (v3.3.0)
"""
# Patch vnai trước khi import vnstock
from ..core import vnstock_patch

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from ..utils.technical_indicators import TechnicalAnalyzer
from ..utils.fundamental_indicators import FundamentalAnalyzer
from ..core.cache import get_cache


class VNStockService:
    """Service tương tác với vnstock API v3.3.0"""

    def __init__(self):
        """Khởi tạo VNStock service"""
        self.stock = None
        self._Vnstock = None
        self.cache = get_cache()

    def _get_vnstock(self):
        """Lazy import Vnstock"""
        if self._Vnstock is None:
            from vnstock import Vnstock
            self._Vnstock = Vnstock()  # Instantiate
        return self._Vnstock

    def get_listing_date(self, symbol: str) -> Optional[str]:
        """
        Lấy ngày niêm yết của cổ phiếu

        Args:
            symbol: Mã cổ phiếu

        Returns:
            Ngày niêm yết dạng string (YYYY-MM-DD) hoặc None
        """
        try:
            if self.stock is None:
                self.stock = self._get_vnstock().stock(symbol=symbol, source='VCI')

            # Sử dụng overview() thay vì profile()
            overview = self.stock.company.overview()

            if overview is not None and not overview.empty:
                # Thử các tên cột khác nhau
                for col in ['listing_date', 'initialListingDate', 'issueDate', 'listingDate']:
                    if col in overview.columns:
                        listing_date = overview[col].iloc[0]
                        if pd.notna(listing_date):
                            return str(listing_date)[:10]  # Lấy YYYY-MM-DD
        except Exception as e:
            print(f"Error getting listing date: {e}")

        # Mặc định 5 năm trước
        return (datetime.now() - timedelta(days=5*365)).strftime('%Y-%m-%d')

    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Lấy thông tin công ty

        Args:
            symbol: Mã cổ phiếu

        Returns:
            Dictionary chứa thông tin công ty
        """
        result = {
            'symbol': symbol.upper(),
            'company_name': None,
            'exchange': None,
            'industry': None,
            'sector': None,
            'listing_date': None,
            'market_cap': None,
            'shares_outstanding': None,
            'website': None,
            'description': None
        }

        try:
            if self.stock is None:
                self.stock = self._get_vnstock().stock(symbol=symbol, source='VCI')

            # Lấy thông tin từ overview (vnstock 3.x không có profile())
            overview = self.stock.company.overview()

            if overview is not None and not overview.empty:
                overview_dict = overview.to_dict('records')[0] if len(overview) > 0 else {}

                # Map các trường dữ liệu từ overview
                field_mappings = {
                    'company_name': ['symbol'],  # Tên công ty (tạm dùng symbol)
                    'industry': ['icb_name3', 'icbName3', 'industry', 'industryName'],
                    'sector': ['icb_name2', 'icbName2', 'sector'],
                    'listing_date': ['listing_date', 'initialListingDate', 'listingDate'],
                    'website': ['website', 'companyWebsite'],
                    'description': ['company_profile', 'companyProfile', 'businessType'],
                    'shares_outstanding': ['issue_share', 'sharesOutstanding', 'financial_ratio_issue_share'],
                    'charter_capital': ['charter_capital']
                }

                for result_key, possible_keys in field_mappings.items():
                    for key in possible_keys:
                        if key in overview_dict and pd.notna(overview_dict[key]):
                            result[result_key] = overview_dict[key]
                            break

            # Lấy exchange từ trading_stats
            try:
                trading_stats = self.stock.company.trading_stats()
                if trading_stats is not None and not trading_stats.empty:
                    stats_dict = trading_stats.to_dict('records')[0]
                    if 'exchange' in stats_dict and pd.notna(stats_dict['exchange']):
                        result['exchange'] = stats_dict['exchange']
            except:
                pass

            # Lấy market cap từ ratio (đơn vị: VND)
            try:
                ratio = self.stock.finance.ratio(period='year', lang='vi')
                if ratio is not None and not ratio.empty:
                    # Market cap trong ratio DataFrame (đã ở đơn vị VND)
                    if ('Chỉ tiêu định giá', 'Vốn hóa (Tỷ đồng)') in ratio.columns:
                        market_cap = ratio[('Chỉ tiêu định giá', 'Vốn hóa (Tỷ đồng)')].iloc[0]
                        if pd.notna(market_cap) and market_cap > 0:
                            # Dữ liệu đã ở dạng VND, không cần nhân thêm
                            result['market_cap'] = float(market_cap)
            except Exception as e:
                print(f"Error getting market cap: {e}")

        except Exception as e:
            print(f"Error getting company info: {e}")

        return result

    def get_price_data(self, symbol: str, start_date: Optional[str] = None,
                      end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Lấy dữ liệu giá lịch sử

        Args:
            symbol: Mã cổ phiếu
            start_date: Ngày bắt đầu (YYYY-MM-DD)
            end_date: Ngày kết thúc (YYYY-MM-DD)

        Returns:
            DataFrame chứa dữ liệu giá
        """
        try:
            if self.stock is None:
                self.stock = self._get_vnstock().stock(symbol=symbol, source='VCI')

            # Nếu không có start_date, lấy từ ngày niêm yết
            if start_date is None:
                start_date = self.get_listing_date(symbol)

            # Nếu không có end_date, lấy đến ngày hiện tại
            if end_date is None:
                end_date = datetime.now().strftime('%Y-%m-%d')

            # Lấy dữ liệu giá
            df = self.stock.quote.history(start=start_date, end=end_date)

            if df is None or df.empty:
                raise ValueError(f"No price data available for {symbol}")

            return df
        except Exception as e:
            print(f"Error getting price data: {e}")
            raise

    def get_financial_statements(self, symbol: str, period: str = 'year',
                                 lang: str = 'vi') -> Dict[str, pd.DataFrame]:
        """
        Lấy báo cáo tài chính

        Args:
            symbol: Mã cổ phiếu
            period: Kỳ báo cáo ('year' hoặc 'quarter')
            lang: Ngôn ngữ ('vi' hoặc 'en')

        Returns:
            Dictionary chứa các báo cáo tài chính
        """
        result = {
            'balance_sheet': pd.DataFrame(),
            'income_statement': pd.DataFrame(),
            'cash_flow': pd.DataFrame(),
            'ratio': pd.DataFrame()
        }

        try:
            if self.stock is None:
                self.stock = self._get_vnstock().stock(symbol=symbol, source='VCI')

            # Lấy báo cáo tài chính
            try:
                balance_sheet = self.stock.finance.balance_sheet(period=period, lang=lang)
                result['balance_sheet'] = balance_sheet if balance_sheet is not None else pd.DataFrame()
            except:
                pass

            try:
                income_statement = self.stock.finance.income_statement(period=period, lang=lang)
                result['income_statement'] = income_statement if income_statement is not None else pd.DataFrame()
            except:
                pass

            try:
                cash_flow = self.stock.finance.cash_flow(period=period, lang=lang)
                result['cash_flow'] = cash_flow if cash_flow is not None else pd.DataFrame()
            except:
                pass

            try:
                ratio = self.stock.finance.ratio(period=period, lang=lang)
                result['ratio'] = ratio if ratio is not None else pd.DataFrame()
            except:
                pass

        except Exception as e:
            print(f"Error getting financial statements: {e}")

        return result

    def get_macro_data(self) -> Dict[str, Any]:
        """
        Lấy dữ liệu kinh tế vĩ mô

        Returns:
            Dictionary chứa các chỉ số kinh tế vĩ mô
        """
        result = {
            'GDP': None,
            'CPI': None,
            'IR': None,
            'EXR': None,
            'UR': None,
            'FGI': None,
            'PCR': None
        }

        # vnstock3 chưa hỗ trợ macro data
        return result

    def get_complete_stock_data(self, symbol: str, start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> Dict[str, Any]:
        """
        Lấy toàn bộ dữ liệu cổ phiếu bao gồm giá, chỉ số kỹ thuật, chỉ số cơ bản

        Args:
            symbol: Mã cổ phiếu
            start_date: Ngày bắt đầu
            end_date: Ngày kết thúc

        Returns:
            Dictionary chứa toàn bộ dữ liệu
        """
        try:
            # 1. Lấy thông tin công ty
            company_info = self.get_company_info(symbol)

            # 2. Lấy dữ liệu giá
            price_df = self.get_price_data(symbol, start_date, end_date)

            # 3. Tính các chỉ số kỹ thuật
            technical_analyzer = TechnicalAnalyzer(price_df)
            technical_indicators = technical_analyzer.calculate_all_indicators()

            # 4. Lấy báo cáo tài chính
            financial_statements = self.get_financial_statements(symbol)

            # 5. Tính các chỉ số cơ bản
            current_price = float(price_df['close'].iloc[-1]) if not price_df.empty else 0

            # Lấy thông tin từ company info hoặc financial statements
            shares_outstanding = company_info.get('shares_outstanding', 1000000)
            market_cap = company_info.get('market_cap', current_price * shares_outstanding if shares_outstanding else 0)

            fundamental_analyzer = FundamentalAnalyzer(financial_statements, price_df)
            fundamental_indicators = fundamental_analyzer.calculate_all_indicators(
                current_price, shares_outstanding, market_cap
            )

            # 6. Lấy dữ liệu vĩ mô
            macro_indicators = self.get_macro_data()

            # 7. Chuyển đổi price data sang dạng list of dict
            price_data = price_df.reset_index().to_dict('records')

            # Chuyển đổi timestamp sang string
            for record in price_data:
                for key, value in record.items():
                    if isinstance(value, pd.Timestamp):
                        record[key] = value.strftime('%Y-%m-%d')
                    elif pd.isna(value):
                        record[key] = None
                    elif isinstance(value, (int, float)):
                        record[key] = float(value) if not pd.isna(value) else None

            # 8. Tổng hợp kết quả
            result = {
                'symbol': symbol.upper(),
                'company_info': company_info,
                'price_data': price_data,
                'technical_indicators': technical_indicators,
                'fundamental_indicators': fundamental_indicators,
                'macro_indicators': macro_indicators,
                'metadata': {
                    'total_records': len(price_data),
                    'start_date': start_date or self.get_listing_date(symbol),
                    'end_date': end_date or datetime.now().strftime('%Y-%m-%d'),
                    'current_price': current_price,
                    'last_updated': datetime.now().isoformat()
                }
            }

            return result
        except Exception as e:
            print(f"Error getting complete stock data: {e}")
            raise
