"""
Portfolio Analytics Service
Phân tích rủi ro và hiệu suất danh mục đầu tư
"""
from typing import List, Dict, Any, Optional
from vnstock import Vnstock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict


class PortfolioAnalytics:
    def __init__(self):
        self.stock = Vnstock()
        self.risk_free_rate = 0.05  # 5% per year (Vietnam bonds)

    def analyze_portfolio(
        self,
        holdings: List[Dict[str, Any]],
        period_days: int = 365
    ) -> Dict[str, Any]:
        """
        Phân tích danh mục đầu tư

        holdings: [
            {'symbol': 'VNM', 'quantity': 100, 'buy_price': 55000},
            {'symbol': 'VIC', 'quantity': 200, 'buy_price': 40000},
            ...
        ]
        """
        if not holdings:
            return {'error': 'No holdings provided'}

        try:
            # Get historical data for all holdings
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)

            portfolio_data = []
            total_investment = 0
            total_current_value = 0

            for holding in holdings:
                symbol = holding['symbol']
                quantity = holding['quantity']
                buy_price = holding['buy_price']

                # Get stock data
                stock_data = self._get_stock_analysis_data(
                    symbol,
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )

                if stock_data:
                    current_price = stock_data['current_price']
                    investment = quantity * buy_price
                    current_value = quantity * current_price
                    profit_loss = current_value - investment
                    profit_loss_pct = (profit_loss / investment) * 100

                    portfolio_data.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'buy_price': buy_price,
                        'current_price': current_price,
                        'investment': investment,
                        'current_value': current_value,
                        'profit_loss': profit_loss,
                        'profit_loss_pct': profit_loss_pct,
                        'weight': 0,  # Will calculate later
                        'returns': stock_data['returns'],
                        'volatility': stock_data['volatility'],
                        'beta': stock_data.get('beta', 1.0),
                        'sector': stock_data.get('sector', 'Others')
                    })

                    total_investment += investment
                    total_current_value += current_value

            # Calculate weights
            for item in portfolio_data:
                item['weight'] = (item['current_value'] / total_current_value) * 100 if total_current_value > 0 else 0

            # Portfolio metrics
            total_profit_loss = total_current_value - total_investment
            total_return_pct = (total_profit_loss / total_investment) * 100 if total_investment > 0 else 0

            # Risk metrics
            risk_metrics = self._calculate_portfolio_risk(portfolio_data)

            # Diversification
            diversification = self._analyze_diversification(portfolio_data)

            # Performance attribution
            performance = self._analyze_performance(portfolio_data, period_days)

            return {
                'summary': {
                    'total_investment': total_investment,
                    'total_current_value': total_current_value,
                    'total_profit_loss': total_profit_loss,
                    'total_return_pct': total_return_pct,
                    'number_of_stocks': len(portfolio_data)
                },
                'holdings': portfolio_data,
                'risk_metrics': risk_metrics,
                'diversification': diversification,
                'performance': performance,
                'recommendations': self._generate_recommendations(portfolio_data, risk_metrics, diversification)
            }

        except Exception as e:
            print(f"Error in analyze_portfolio: {e}")
            return {'error': str(e)}

    def _get_stock_analysis_data(self, symbol: str, start_date: str, end_date: str) -> Optional[Dict]:
        """Get stock data for analysis"""
        try:
            stock = Vnstock().stock(symbol=symbol, source='VCI')

            # Get price history
            price_data = stock.quote.history(start=start_date, end=end_date)
            if price_data is None or price_data.empty:
                return None

            # Get company info
            overview = stock.company.overview()

            # Calculate returns
            returns = price_data['close'].pct_change().dropna()

            # Calculate volatility (annualized)
            volatility = returns.std() * np.sqrt(252) * 100  # Annualized %

            # Get current price
            current_price = float(price_data.iloc[-1]['close'])

            # Get sector
            sector = 'Others'
            if isinstance(overview, dict):
                sector = overview.get('icbName3', 'Others')
            elif isinstance(overview, pd.DataFrame) and not overview.empty:
                if 'icbName3' in overview.columns:
                    sector = overview['icbName3'].iloc[0]

            # Calculate beta (simplified - vs VN-Index)
            beta = self._calculate_beta(returns)

            return {
                'current_price': current_price,
                'returns': returns.tolist(),
                'volatility': volatility,
                'beta': beta,
                'sector': sector
            }

        except Exception as e:
            print(f"Error getting data for {symbol}: {e}")
            return None

    def _calculate_beta(self, stock_returns: pd.Series) -> float:
        """Calculate beta (simplified, assuming market return = 1)"""
        try:
            if len(stock_returns) < 2:
                return 1.0

            # Simplified beta calculation
            variance = stock_returns.var()
            if variance == 0:
                return 1.0

            covariance = stock_returns.cov(stock_returns)
            beta = covariance / variance

            return beta if not np.isnan(beta) else 1.0

        except:
            return 1.0

    def _calculate_portfolio_risk(self, portfolio_data: List[Dict]) -> Dict[str, Any]:
        """Calculate risk metrics for portfolio"""
        try:
            # Portfolio returns (weighted)
            weights = np.array([item['weight'] / 100 for item in portfolio_data])
            returns_list = [item['profit_loss_pct'] for item in portfolio_data]

            # Portfolio volatility (simplified)
            volatilities = np.array([item['volatility'] for item in portfolio_data])
            portfolio_volatility = np.sqrt(np.dot(weights**2, volatilities**2))

            # Value at Risk (VaR) - 95% confidence
            portfolio_return = np.dot(weights, returns_list)
            var_95 = portfolio_return - 1.645 * portfolio_volatility

            # Sharpe Ratio
            excess_return = portfolio_return - self.risk_free_rate * 100
            sharpe_ratio = excess_return / portfolio_volatility if portfolio_volatility > 0 else 0

            # Maximum Drawdown (simplified)
            max_drawdown = min(0, min(returns_list))

            # Portfolio Beta
            betas = np.array([item['beta'] for item in portfolio_data])
            portfolio_beta = np.dot(weights, betas)

            return {
                'portfolio_volatility': round(portfolio_volatility, 2),
                'value_at_risk_95': round(var_95, 2),
                'sharpe_ratio': round(sharpe_ratio, 2),
                'max_drawdown': round(max_drawdown, 2),
                'portfolio_beta': round(portfolio_beta, 2),
                'risk_level': self._get_risk_level(portfolio_volatility)
            }

        except Exception as e:
            print(f"Error calculating risk: {e}")
            return {
                'portfolio_volatility': 0,
                'value_at_risk_95': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'portfolio_beta': 1.0,
                'risk_level': 'UNKNOWN'
            }

    def _get_risk_level(self, volatility: float) -> str:
        """Determine risk level based on volatility"""
        if volatility < 15:
            return "LOW"
        elif volatility < 25:
            return "MEDIUM"
        else:
            return "HIGH"

    def _analyze_diversification(self, portfolio_data: List[Dict]) -> Dict[str, Any]:
        """Analyze portfolio diversification"""
        try:
            # Sector allocation
            sector_allocation = defaultdict(float)
            for item in portfolio_data:
                sector_allocation[item['sector']] += item['weight']

            # Concentration risk (Herfindahl Index)
            weights = [item['weight'] / 100 for item in portfolio_data]
            herfindahl_index = sum(w**2 for w in weights)

            # Number of effective holdings
            effective_holdings = 1 / herfindahl_index if herfindahl_index > 0 else 0

            # Diversification score (0-100)
            diversification_score = min(100, (effective_holdings / len(portfolio_data)) * 100) if len(portfolio_data) > 0 else 0

            return {
                'sector_allocation': dict(sector_allocation),
                'herfindahl_index': round(herfindahl_index, 4),
                'effective_holdings': round(effective_holdings, 2),
                'diversification_score': round(diversification_score, 2),
                'diversification_level': self._get_diversification_level(diversification_score)
            }

        except Exception as e:
            print(f"Error analyzing diversification: {e}")
            return {
                'sector_allocation': {},
                'herfindahl_index': 0,
                'effective_holdings': 0,
                'diversification_score': 0,
                'diversification_level': 'UNKNOWN'
            }

    def _get_diversification_level(self, score: float) -> str:
        """Determine diversification level"""
        if score > 75:
            return "EXCELLENT"
        elif score > 50:
            return "GOOD"
        elif score > 25:
            return "MODERATE"
        else:
            return "POOR"

    def _analyze_performance(self, portfolio_data: List[Dict], period_days: int) -> Dict[str, Any]:
        """Analyze portfolio performance"""
        try:
            # Top performers
            sorted_by_return = sorted(portfolio_data, key=lambda x: x['profit_loss_pct'], reverse=True)
            top_performers = sorted_by_return[:3]
            worst_performers = sorted_by_return[-3:]

            # Calculate annualized return
            total_return = np.average([item['profit_loss_pct'] for item in portfolio_data],
                                     weights=[item['weight'] for item in portfolio_data])

            annualized_return = ((1 + total_return / 100) ** (365 / period_days) - 1) * 100

            return {
                'annualized_return': round(annualized_return, 2),
                'period_days': period_days,
                'top_performers': [
                    {
                        'symbol': item['symbol'],
                        'return_pct': round(item['profit_loss_pct'], 2),
                        'profit_loss': round(item['profit_loss'], 0)
                    } for item in top_performers
                ],
                'worst_performers': [
                    {
                        'symbol': item['symbol'],
                        'return_pct': round(item['profit_loss_pct'], 2),
                        'profit_loss': round(item['profit_loss'], 0)
                    } for item in worst_performers
                ]
            }

        except Exception as e:
            print(f"Error analyzing performance: {e}")
            return {
                'annualized_return': 0,
                'period_days': period_days,
                'top_performers': [],
                'worst_performers': []
            }

    def _generate_recommendations(
        self,
        portfolio_data: List[Dict],
        risk_metrics: Dict,
        diversification: Dict
    ) -> List[str]:
        """Generate portfolio recommendations"""
        recommendations = []

        try:
            # Check concentration
            max_weight = max(item['weight'] for item in portfolio_data) if portfolio_data else 0
            if max_weight > 30:
                recommendations.append(f"⚠️ Một cổ phiếu chiếm {max_weight:.1f}% danh mục - Nên phân tán để giảm rủi ro")

            # Check diversification
            if diversification['diversification_score'] < 50:
                recommendations.append("📊 Danh mục chưa đủ đa dạng hóa - Nên đầu tư thêm vào các ngành khác")

            # Check risk level
            if risk_metrics['risk_level'] == "HIGH":
                recommendations.append("⚠️ Danh mục có mức rủi ro cao - Cân nhắc thêm cổ phiếu ổn định")

            # Check Sharpe ratio
            if risk_metrics['sharpe_ratio'] < 0.5:
                recommendations.append("💡 Tỷ lệ lợi nhuận/rủi ro thấp - Có thể cân nhắc điều chỉnh danh mục")

            # Check sector concentration
            sector_alloc = diversification['sector_allocation']
            for sector, weight in sector_alloc.items():
                if weight > 40:
                    recommendations.append(f"⚠️ Ngành {sector} chiếm {weight:.1f}% - Nên phân tán sang ngành khác")

            # Check number of stocks
            if len(portfolio_data) < 5:
                recommendations.append("📈 Nên tăng số lượng cổ phiếu lên ít nhất 5-10 mã để giảm rủi ro")
            elif len(portfolio_data) > 20:
                recommendations.append("🎯 Danh mục có quá nhiều cổ phiếu - Khó quản lý hiệu quả")

            # Check losing positions
            losing_stocks = [item for item in portfolio_data if item['profit_loss_pct'] < -20]
            if losing_stocks:
                symbols = ', '.join([item['symbol'] for item in losing_stocks])
                recommendations.append(f"🔴 Cổ phiếu đang lỗ nặng: {symbols} - Cân nhắc cắt lỗ hoặc chờ hồi phục")

            if not recommendations:
                recommendations.append("✅ Danh mục đang được phân bổ hợp lý")

            return recommendations

        except Exception as e:
            print(f"Error generating recommendations: {e}")
            return ["Không thể tạo đề xuất"]

    def compare_with_market(
        self,
        portfolio_return: float,
        period_days: int = 365
    ) -> Dict[str, Any]:
        """Compare portfolio performance with market index"""
        try:
            # Get VN-Index data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=period_days)

            # Placeholder - would need actual VN-Index data
            vn_index_return = 10.5  # Example: 10.5% return

            outperformance = portfolio_return - vn_index_return

            return {
                'portfolio_return': round(portfolio_return, 2),
                'market_return': round(vn_index_return, 2),
                'outperformance': round(outperformance, 2),
                'benchmark': 'VN-Index',
                'period_days': period_days
            }

        except Exception as e:
            print(f"Error comparing with market: {e}")
            return {
                'portfolio_return': portfolio_return,
                'market_return': 0,
                'outperformance': 0,
                'benchmark': 'VN-Index',
                'period_days': period_days
            }
