"""
Module tính toán các chỉ số cơ bản và tài chính (Fundamental Indicators)
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional


class FundamentalAnalyzer:
    """Class phân tích cơ bản"""

    def __init__(self, financial_data: Dict[str, Any], price_data: Optional[pd.DataFrame] = None):
        """
        Khởi tạo với dữ liệu tài chính

        Args:
            financial_data: Dictionary chứa dữ liệu tài chính từ vnstock
            price_data: DataFrame chứa dữ liệu giá (optional)
        """
        self.financial_data = financial_data
        self.price_data = price_data

    @staticmethod
    def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
        """
        Chia an toàn, tránh chia cho 0

        Args:
            numerator: Số bị chia
            denominator: Số chia
            default: Giá trị mặc định nếu chia cho 0

        Returns:
            Kết quả phép chia hoặc giá trị mặc định
        """
        try:
            if denominator == 0 or pd.isna(denominator) or pd.isna(numerator):
                return default
            result = numerator / denominator
            return result if not pd.isna(result) else default
        except:
            return default

    def calculate_eps(self, net_income: float, shares_outstanding: float) -> float:
        """
        Tính EPS (Earnings Per Share)

        Args:
            net_income: Lợi nhuận ròng
            shares_outstanding: Số cổ phiếu đang lưu hành

        Returns:
            EPS
        """
        return self.safe_divide(net_income, shares_outstanding)

    def calculate_pe(self, price: float, eps: float) -> float:
        """
        Tính P/E (Price to Earnings Ratio)

        Args:
            price: Giá cổ phiếu
            eps: Thu nhập trên mỗi cổ phiếu

        Returns:
            P/E ratio
        """
        return self.safe_divide(price, eps)

    def calculate_pb(self, price: float, book_value_per_share: float) -> float:
        """
        Tính P/B (Price to Book Ratio)

        Args:
            price: Giá cổ phiếu
            book_value_per_share: Giá trị sổ sách trên mỗi cổ phiếu

        Returns:
            P/B ratio
        """
        return self.safe_divide(price, book_value_per_share)

    def calculate_ps(self, market_cap: float, revenue: float) -> float:
        """
        Tính P/S (Price to Sales Ratio)

        Args:
            market_cap: Vốn hóa thị trường
            revenue: Doanh thu

        Returns:
            P/S ratio
        """
        return self.safe_divide(market_cap, revenue)

    def calculate_pcf(self, price: float, cash_flow_per_share: float) -> float:
        """
        Tính P/CF (Price to Cash Flow Ratio)

        Args:
            price: Giá cổ phiếu
            cash_flow_per_share: Dòng tiền trên mỗi cổ phiếu

        Returns:
            P/CF ratio
        """
        return self.safe_divide(price, cash_flow_per_share)

    def calculate_dividend_yield(self, dividend_per_share: float, price: float) -> float:
        """
        Tính Dividend Yield

        Args:
            dividend_per_share: Cổ tức trên mỗi cổ phiếu
            price: Giá cổ phiếu

        Returns:
            Dividend Yield (%)
        """
        return self.safe_divide(dividend_per_share, price) * 100

    def calculate_ev_ebitda(self, enterprise_value: float, ebitda: float) -> float:
        """
        Tính EV/EBITDA

        Args:
            enterprise_value: Giá trị doanh nghiệp
            ebitda: EBITDA

        Returns:
            EV/EBITDA ratio
        """
        return self.safe_divide(enterprise_value, ebitda)

    def calculate_peg(self, pe_ratio: float, earnings_growth_rate: float) -> float:
        """
        Tính PEG (Price/Earnings to Growth Ratio)

        Args:
            pe_ratio: P/E ratio
            earnings_growth_rate: Tốc độ tăng trưởng lợi nhuận (%)

        Returns:
            PEG ratio
        """
        return self.safe_divide(pe_ratio, earnings_growth_rate)

    def calculate_roe(self, net_income: float, shareholders_equity: float) -> float:
        """
        Tính ROE (Return on Equity)

        Args:
            net_income: Lợi nhuận ròng
            shareholders_equity: Vốn chủ sở hữu

        Returns:
            ROE (%)
        """
        return self.safe_divide(net_income, shareholders_equity) * 100

    def calculate_roa(self, net_income: float, total_assets: float) -> float:
        """
        Tính ROA (Return on Assets)

        Args:
            net_income: Lợi nhuận ròng
            total_assets: Tổng tài sản

        Returns:
            ROA (%)
        """
        return self.safe_divide(net_income, total_assets) * 100

    def calculate_de(self, total_debt: float, shareholders_equity: float) -> float:
        """
        Tính D/E (Debt to Equity Ratio)

        Args:
            total_debt: Tổng nợ
            shareholders_equity: Vốn chủ sở hữu

        Returns:
            D/E ratio
        """
        return self.safe_divide(total_debt, shareholders_equity)

    def calculate_current_ratio(self, current_assets: float, current_liabilities: float) -> float:
        """
        Tính Current Ratio

        Args:
            current_assets: Tài sản ngắn hạn
            current_liabilities: Nợ ngắn hạn

        Returns:
            Current Ratio
        """
        return self.safe_divide(current_assets, current_liabilities)

    def calculate_npm(self, net_income: float, revenue: float) -> float:
        """
        Tính NPM (Net Profit Margin)

        Args:
            net_income: Lợi nhuận ròng
            revenue: Doanh thu

        Returns:
            NPM (%)
        """
        return self.safe_divide(net_income, revenue) * 100

    def calculate_revenue_growth(self, current_revenue: float, previous_revenue: float) -> float:
        """
        Tính Revenue Growth

        Args:
            current_revenue: Doanh thu kỳ hiện tại
            previous_revenue: Doanh thu kỳ trước

        Returns:
            Revenue Growth (%)
        """
        if previous_revenue == 0:
            return 0
        return ((current_revenue - previous_revenue) / previous_revenue) * 100

    def calculate_fcf(self, operating_cash_flow: float, capital_expenditure: float) -> float:
        """
        Tính FCF (Free Cash Flow)

        Args:
            operating_cash_flow: Dòng tiền hoạt động
            capital_expenditure: Chi phí vốn

        Returns:
            FCF
        """
        return operating_cash_flow - capital_expenditure

    def extract_from_balance_sheet(self, balance_sheet: pd.DataFrame) -> Dict[str, float]:
        """
        Trích xuất dữ liệu từ bảng cân đối kế toán

        Args:
            balance_sheet: DataFrame bảng cân đối kế toán

        Returns:
            Dictionary chứa các chỉ số từ BCĐKT
        """
        if balance_sheet is None or balance_sheet.empty:
            return {}

        try:
            # Lấy dữ liệu kỳ gần nhất (cột cuối cùng)
            latest_data = balance_sheet.iloc[:, -1]

            result = {}

            # Mapping các chỉ tiêu (cần điều chỉnh theo cấu trúc thực tế của vnstock)
            mappings = {
                'total_assets': ['Tổng tài sản', 'Total Assets', 'TÀI SẢN'],
                'current_assets': ['Tài sản ngắn hạn', 'Current Assets', 'TÀI SẢN NGẮN HẠN'],
                'current_liabilities': ['Nợ ngắn hạn', 'Current Liabilities', 'NỢ NGẮN HẠN'],
                'total_debt': ['Tổng nợ', 'Total Debt', 'TỔNG NỢ PHẢI TRẢ'],
                'shareholders_equity': ['Vốn chủ sở hữu', 'Shareholders Equity', 'VỐN CHỦ SỞ HỮU']
            }

            for key, possible_names in mappings.items():
                for name in possible_names:
                    if name in balance_sheet.index:
                        result[key] = float(latest_data[name]) if pd.notna(latest_data[name]) else 0
                        break
                if key not in result:
                    result[key] = 0

            return result
        except Exception as e:
            print(f"Error extracting balance sheet data: {e}")
            return {}

    def extract_from_income_statement(self, income_statement: pd.DataFrame) -> Dict[str, float]:
        """
        Trích xuất dữ liệu từ báo cáo kết quả kinh doanh

        Args:
            income_statement: DataFrame báo cáo kết quả kinh doanh

        Returns:
            Dictionary chứa các chỉ số từ BCKQKD
        """
        if income_statement is None or income_statement.empty:
            return {}

        try:
            # Lấy dữ liệu kỳ gần nhất và kỳ trước
            latest_data = income_statement.iloc[:, -1]
            previous_data = income_statement.iloc[:, -2] if len(income_statement.columns) > 1 else None

            result = {}

            # Mapping các chỉ tiêu
            mappings = {
                'revenue': ['Doanh thu', 'Revenue', 'DOANH THU BÁN HÀNG'],
                'net_income': ['Lợi nhuận sau thuế', 'Net Income', 'LỢI NHUẬN SAU THUẾ'],
                'ebitda': ['EBITDA', 'Lợi nhuận trước thuế và lãi vay'],
                'gross_profit': ['Lợi nhuận gộp', 'Gross Profit']
            }

            for key, possible_names in mappings.items():
                for name in possible_names:
                    if name in income_statement.index:
                        result[key] = float(latest_data[name]) if pd.notna(latest_data[name]) else 0
                        if previous_data is not None and name in income_statement.index:
                            result[f'previous_{key}'] = float(previous_data[name]) if pd.notna(previous_data[name]) else 0
                        break
                if key not in result:
                    result[key] = 0

            return result
        except Exception as e:
            print(f"Error extracting income statement data: {e}")
            return {}

    def extract_from_cash_flow(self, cash_flow: pd.DataFrame) -> Dict[str, float]:
        """
        Trích xuất dữ liệu từ báo cáo lưu chuyển tiền tệ

        Args:
            cash_flow: DataFrame báo cáo lưu chuyển tiền tệ

        Returns:
            Dictionary chứa các chỉ số từ BCLCTT
        """
        if cash_flow is None or cash_flow.empty:
            return {}

        try:
            # Lấy dữ liệu kỳ gần nhất (dòng đầu tiên)
            latest_data = cash_flow.iloc[0]

            result = {}

            # Mapping các chỉ tiêu
            mappings = {
                'operating_cash_flow': [
                    'Lưu chuyển tiền tệ ròng từ các hoạt động SXKD',
                    'Lưu chuyển tiền từ hoạt động kinh doanh',
                    'Operating Cash Flow',
                    'OCF'
                ],
                'investing_cash_flow': [
                    'Lưu chuyển từ hoạt động đầu tư',
                    'Lưu chuyển tiền từ hoạt động đầu tư',
                    'Investing Cash Flow'
                ],
                'financing_cash_flow': [
                    'Lưu chuyển tiền từ hoạt động tài chính',
                    'Financing Cash Flow'
                ],
                'capital_expenditure': [
                    'Mua sắm TSCĐ',
                    'Chi phí vốn',
                    'Capital Expenditure',
                    'CAPEX'
                ]
            }

            # Tìm trong columns thay vì index
            for key, possible_names in mappings.items():
                for name in possible_names:
                    if name in cash_flow.columns:
                        result[key] = float(latest_data[name]) if pd.notna(latest_data[name]) else 0
                        break
                if key not in result:
                    result[key] = 0

            return result
        except Exception as e:
            print(f"Error extracting cash flow data: {e}")
            return {}

    def extract_from_ratio(self, ratio_df: pd.DataFrame) -> Dict[str, float]:
        """
        Trích xuất dữ liệu từ DataFrame ratio của vnstock (có multi-level columns)

        Args:
            ratio_df: DataFrame chứa các chỉ số tài chính từ vnstock

        Returns:
            Dictionary chứa các chỉ số tài chính
        """
        if ratio_df is None or ratio_df.empty:
            return {}

        try:
            result = {}

            # Lấy dòng gần nhất (dòng đầu tiên)
            latest_row = ratio_df.iloc[0]

            # Mapping các chỉ tiêu với multi-level column names
            # Format: (category, indicator_name)
            mappings = {
                'EPS': [
                    ('Chỉ tiêu định giá', 'EPS (VND)'),
                    ('Valuation', 'EPS'),
                ],
                'PE': [
                    ('Chỉ tiêu định giá', 'P/E'),
                    ('Valuation', 'P/E'),
                ],
                'PB': [
                    ('Chỉ tiêu định giá', 'P/B'),
                    ('Valuation', 'P/B'),
                ],
                'PS': [
                    ('Chỉ tiêu định giá', 'P/S'),
                    ('Valuation', 'P/S'),
                ],
                'PCF': [
                    ('Chỉ tiêu định giá', 'P/Cash Flow'),
                    ('Valuation', 'P/CF'),
                ],
                'BVPS': [
                    ('Chỉ tiêu định giá', 'BVPS (VND)'),
                    ('Valuation', 'BVPS'),
                ],
                'EV_EBITDA': [
                    ('Chỉ tiêu định giá', 'EV/EBITDA'),
                    ('Valuation', 'EV/EBITDA'),
                ],
                'ROE': [
                    ('Chỉ tiêu khả năng sinh lợi', 'ROE (%)'),
                    ('Profitability', 'ROE'),
                ],
                'ROA': [
                    ('Chỉ tiêu khả năng sinh lợi', 'ROA (%)'),
                    ('Profitability', 'ROA'),
                ],
                'ROIC': [
                    ('Chỉ tiêu khả năng sinh lợi', 'ROIC (%)'),
                    ('Profitability', 'ROIC'),
                ],
                'NPM': [
                    ('Chỉ tiêu khả năng sinh lợi', 'Biên lợi nhuận ròng (%)'),
                    ('Profitability', 'Net Profit Margin'),
                ],
                'GPM': [
                    ('Chỉ tiêu khả năng sinh lợi', 'Biên lợi nhuận gộp (%)'),
                    ('Profitability', 'Gross Profit Margin'),
                ],
                'EBIT_MARGIN': [
                    ('Chỉ tiêu khả năng sinh lợi', 'Biên EBIT (%)'),
                    ('Profitability', 'EBIT Margin'),
                ],
                'EBITDA': [
                    ('Chỉ tiêu khả năng sinh lợi', 'EBITDA (Tỷ đồng)'),
                    ('Profitability', 'EBITDA'),
                ],
                'EBIT': [
                    ('Chỉ tiêu khả năng sinh lợi', 'EBIT (Tỷ đồng)'),
                    ('Profitability', 'EBIT'),
                ],
                'DE': [
                    ('Chỉ tiêu cơ cấu nguồn vốn', 'Nợ/VCSH'),
                    ('Capital Structure', 'D/E'),
                ],
                'CR': [
                    ('Chỉ tiêu thanh khoản', 'Chỉ số thanh toán hiện thời'),
                    ('Liquidity', 'Current Ratio'),
                ],
                'QUICK_RATIO': [
                    ('Chỉ tiêu thanh khoản', 'Chỉ số thanh toán nhanh'),
                    ('Liquidity', 'Quick Ratio'),
                ],
                'CASH_RATIO': [
                    ('Chỉ tiêu thanh khoản', 'Chỉ số thanh toán tiền mặt'),
                    ('Liquidity', 'Cash Ratio'),
                ],
                'DY': [
                    ('Chỉ tiêu khả năng sinh lợi', 'Tỷ suất cổ tức (%)'),
                    ('Chỉ tiêu định giá', 'Tỷ suất cổ tức (%)'),
                    ('Valuation', 'Dividend Yield'),
                ],
                'MARKET_CAP': [
                    ('Chỉ tiêu định giá', 'Vốn hóa (Tỷ đồng)'),
                    ('Valuation', 'Market Cap'),
                ],
                'SHARES_OUTSTANDING': [
                    ('Chỉ tiêu định giá', 'Số CP lưu hành (Triệu CP)'),
                    ('Valuation', 'Shares Outstanding'),
                ],
            }

            # Extract data từ multi-level columns
            for key, possible_columns in mappings.items():
                for col in possible_columns:
                    if col in ratio_df.columns:
                        value = latest_row[col]
                        if pd.notna(value):
                            result[key] = float(value)
                            break

            return result
        except Exception as e:
            print(f"Error extracting ratio data: {e}")
            return {}

    def calculate_all_indicators(self, price: float, shares_outstanding: float,
                                market_cap: float) -> Dict[str, Any]:
        """
        Tính toán tất cả các chỉ số cơ bản

        Args:
            price: Giá cổ phiếu hiện tại
            shares_outstanding: Số cổ phiếu đang lưu hành
            market_cap: Vốn hóa thị trường

        Returns:
            Dictionary chứa tất cả các chỉ số cơ bản
        """
        # Ưu tiên lấy từ ratio DataFrame (vnstock 3.x)
        ratio_data = self.extract_from_ratio(
            self.financial_data.get('ratio')
        )

        # Trích xuất dữ liệu từ các báo cáo tài chính (fallback)
        balance_sheet_data = self.extract_from_balance_sheet(
            self.financial_data.get('balance_sheet')
        )
        income_statement_data = self.extract_from_income_statement(
            self.financial_data.get('income_statement')
        )
        cash_flow_data = self.extract_from_cash_flow(
            self.financial_data.get('cash_flow')
        )

        # Tính toán các chỉ số (nếu không có trong ratio)
        eps = ratio_data.get('EPS') or self.calculate_eps(
            income_statement_data.get('net_income', 0),
            shares_outstanding
        )

        book_value = balance_sheet_data.get('shareholders_equity', 0)
        book_value_per_share = self.safe_divide(book_value, shares_outstanding)

        ocf = cash_flow_data.get('operating_cash_flow', 0)
        capex = cash_flow_data.get('capital_expenditure', 0)
        fcf = self.calculate_fcf(ocf, capex)

        revenue = income_statement_data.get('revenue', 0)
        previous_revenue = income_statement_data.get('previous_revenue', 0)
        revenue_growth = self.calculate_revenue_growth(revenue, previous_revenue)

        # Kết hợp data từ ratio và tính toán
        result = {
            'EPS': round(ratio_data.get('EPS', eps), 2) if ratio_data.get('EPS') or eps else None,
            'PE': round(ratio_data.get('PE', 0), 2) if ratio_data.get('PE') else (round(self.calculate_pe(price, eps), 2) if eps else None),
            'PB': round(ratio_data.get('PB', 0), 2) if ratio_data.get('PB') else (round(self.calculate_pb(price, book_value_per_share), 2) if book_value_per_share else None),
            'PS': round(ratio_data.get('PS', 0), 2) if ratio_data.get('PS') else (round(self.calculate_ps(market_cap, revenue), 2) if revenue else None),
            'PCF': round(ratio_data.get('PCF', 0), 2) if ratio_data.get('PCF') else None,
            'DY': round(ratio_data.get('DY', 0), 2) if ratio_data.get('DY') else None,
            'EV_EBITDA': round(ratio_data.get('EV_EBITDA', 0), 2) if ratio_data.get('EV_EBITDA') else None,
            'PEG': None,  # Cần thêm dữ liệu tăng trưởng earnings
            'ROE': round(ratio_data.get('ROE', 0), 2) if ratio_data.get('ROE') else round(self.calculate_roe(
                income_statement_data.get('net_income', 0),
                balance_sheet_data.get('shareholders_equity', 1)
            ), 2),
            'ROA': round(ratio_data.get('ROA', 0), 2) if ratio_data.get('ROA') else round(self.calculate_roa(
                income_statement_data.get('net_income', 0),
                balance_sheet_data.get('total_assets', 1)
            ), 2),
            'DE': round(ratio_data.get('DE', 0), 2) if ratio_data.get('DE') else round(self.calculate_de(
                balance_sheet_data.get('total_debt', 0),
                balance_sheet_data.get('shareholders_equity', 1)
            ), 2),
            'CR': round(ratio_data.get('CR', 0), 2) if ratio_data.get('CR') else round(self.calculate_current_ratio(
                balance_sheet_data.get('current_assets', 0),
                balance_sheet_data.get('current_liabilities', 1)
            ), 2),
            'NPM': round(ratio_data.get('NPM', 0), 2) if ratio_data.get('NPM') else (round(self.calculate_npm(
                income_statement_data.get('net_income', 0),
                revenue
            ), 2) if revenue else None),
            'RG': round(revenue_growth, 2) if revenue_growth else None,
            'OCF': ocf,
            'FCF': fcf
        }

        # Thêm các chỉ số bổ sung từ ratio nếu có
        additional_indicators = ['ROIC', 'GPM', 'EBIT_MARGIN', 'EBITDA', 'EBIT',
                                 'QUICK_RATIO', 'CASH_RATIO', 'BVPS', 'MARKET_CAP',
                                 'SHARES_OUTSTANDING']
        for indicator in additional_indicators:
            if indicator in ratio_data:
                result[indicator] = round(ratio_data[indicator], 2) if ratio_data[indicator] else None

        return result
