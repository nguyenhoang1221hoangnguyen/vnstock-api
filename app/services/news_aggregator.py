"""
News Aggregator Service
Tổng hợp tin tức từ nhiều nguồn về cổ phiếu và thị trường
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import re


class NewsAggregator:
    def __init__(self):
        self.sources = {
            'cafef': 'https://cafef.vn',
            'vietstock': 'https://vietstock.vn',
            'ndh': 'https://ndh.vn',
            'zing': 'https://zingnews.vn/kinh-doanh-tai-chinh.html'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def get_latest_news(
        self,
        symbol: Optional[str] = None,
        limit: int = 20,
        sources: List[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lấy tin tức mới nhất

        symbol: Mã cổ phiếu (None = tin tổng hợp)
        limit: Số lượng tin tức
        sources: Danh sách nguồn tin
        """
        if sources is None:
            sources = list(self.sources.keys())

        all_news = []

        for source in sources:
            try:
                if source == 'cafef':
                    news = self._fetch_cafef_news(symbol, limit)
                elif source == 'vietstock':
                    news = self._fetch_vietstock_news(symbol, limit)
                elif source == 'mock':  # Mock data for testing
                    news = self._get_mock_news(symbol, limit)
                else:
                    news = []

                all_news.extend(news)

            except Exception as e:
                print(f"Error fetching from {source}: {e}")
                continue

        # Sort by timestamp
        all_news.sort(key=lambda x: x.get('timestamp', ''), reverse=True)

        # Add sentiment score (mock for now)
        for news_item in all_news:
            news_item['sentiment'] = self._analyze_sentiment(news_item['title'] + ' ' + news_item.get('description', ''))

        return all_news[:limit]

    def _fetch_cafef_news(self, symbol: Optional[str], limit: int) -> List[Dict]:
        """Fetch news from CafeF (mock implementation)"""
        # In production, would use actual scraping
        return self._get_mock_news(symbol, limit // 4, source='CafeF')

    def _fetch_vietstock_news(self, symbol: Optional[str], limit: int) -> List[Dict]:
        """Fetch news from Vietstock (mock implementation)"""
        return self._get_mock_news(symbol, limit // 4, source='Vietstock')

    def _get_mock_news(self, symbol: Optional[str], limit: int, source: str = 'Mock') -> List[Dict]:
        """Generate mock news data"""
        base_time = datetime.now()

        if symbol:
            news_templates = [
                {
                    'title': f'{symbol}: Kết quả kinh doanh quý {(datetime.now().month-1)//3 + 1} vượt kỳ vọng',
                    'description': f'Doanh thu và lợi nhuận của {symbol} tăng trưởng mạnh so với cùng kỳ năm trước.',
                    'category': 'Kết quả kinh doanh',
                    'sentiment_text': 'positive'
                },
                {
                    'title': f'{symbol}: Cổ đông lớn đăng ký mua vào 5 triệu cổ phiếu',
                    'description': f'Cổ đông chiến lược đăng ký mua thêm cổ phiếu {symbol} trong tháng tới.',
                    'category': 'Giao dịch nội bộ',
                    'sentiment_text': 'positive'
                },
                {
                    'title': f'{symbol}: Tăng trưởng doanh thu ấn tượng trong 6 tháng đầu năm',
                    'description': f'{symbol} công bố kết quả kinh doanh 6 tháng với mức tăng trưởng vượt kế hoạch.',
                    'category': 'Báo cáo tài chính',
                    'sentiment_text': 'positive'
                },
                {
                    'title': f'Phân tích {symbol}: Triển vọng tích cực trong quý tới',
                    'description': f'Các chuyên gia nhận định {symbol} có tiềm năng tăng trưởng tốt.',
                    'category': 'Phân tích',
                    'sentiment_text': 'positive'
                },
                {
                    'title': f'{symbol}: Đối mặt với áp lực cạnh tranh trong ngành',
                    'description': f'Thị trường ngày càng khốc liệt khiến {symbol} gặp khó khăn.',
                    'category': 'Phân tích',
                    'sentiment_text': 'negative'
                }
            ]
        else:
            news_templates = [
                {
                    'title': 'VN-Index tăng điểm mạnh trong phiên sáng',
                    'description': 'Thị trường chứng khoán Việt Nam giao dịch sôi động với thanh khoản cao.',
                    'category': 'Thị trường',
                    'sentiment_text': 'positive'
                },
                {
                    'title': 'Dòng tiền ngoại tiếp tục đổ vào thị trường chứng khoán',
                    'description': 'Nhà đầu tư nước ngoài mua ròng mạnh trong tuần qua.',
                    'category': 'Dòng tiền',
                    'sentiment_text': 'positive'
                },
                {
                    'title': 'Cổ phiếu ngân hàng dẫn dắt thị trường tăng điểm',
                    'description': 'Nhóm cổ phiếu ngân hàng tăng trần hàng loạt.',
                    'category': 'Thị trường',
                    'sentiment_text': 'positive'
                },
                {
                    'title': 'NHNN giữ nguyên lãi suất điều hành',
                    'description': 'Ngân hàng Nhà nước quyết định giữ nguyên các mức lãi suất.',
                    'category': 'Chính sách',
                    'sentiment_text': 'neutral'
                },
                {
                    'title': 'GDP quý 1 tăng trưởng 6.5%',
                    'description': 'Nền kinh tế Việt Nam tiếp tục duy trì đà tăng trưởng.',
                    'category': 'Kinh tế',
                    'sentiment_text': 'positive'
                },
                {
                    'title': 'Áp lực bán từ nhà đầu tư cá nhân tăng cao',
                    'description': 'Nhiều nhà đầu tư cá nhân chốt lời khiến thị trường điều chỉnh.',
                    'category': 'Thị trường',
                    'sentiment_text': 'negative'
                }
            ]

        news_list = []
        for i in range(min(limit, len(news_templates))):
            template = news_templates[i % len(news_templates)]
            timestamp = (base_time - timedelta(hours=i*2, minutes=i*15)).isoformat()

            news_list.append({
                'id': f'{source}_{symbol or "market"}_{i}_{int(datetime.now().timestamp())}',
                'title': template['title'],
                'description': template['description'],
                'url': f'{self.sources.get(source.lower(), "#")}',
                'source': source,
                'category': template['category'],
                'timestamp': timestamp,
                'published_time': self._format_time_ago(base_time - timedelta(hours=i*2, minutes=i*15)),
                'symbol': symbol,
                'sentiment_text': template['sentiment_text']
            })

        return news_list

    def _format_time_ago(self, dt: datetime) -> str:
        """Format time as 'X hours ago'"""
        now = datetime.now()
        diff = now - dt

        if diff.days > 0:
            return f"{diff.days} ngày trước"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} giờ trước"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} phút trước"
        else:
            return "Vừa xong"

    def _analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of news (simplified)
        In production, would use NLP model
        """
        # Simple keyword-based sentiment
        positive_keywords = [
            'tăng', 'tích cực', 'tốt', 'cao', 'mạnh', 'vượt', 'lợi nhuận',
            'tăng trưởng', 'thành công', 'khả quan', 'ấn tượng', 'đột phá'
        ]
        negative_keywords = [
            'giảm', 'sụt', 'tiêu cực', 'xấu', 'thấp', 'yếu', 'lỗ', 'khó khăn',
            'suy giảm', 'thất bại', 'rủi ro', 'áp lực', 'lo ngại'
        ]

        text_lower = text.lower()

        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)

        if positive_count > negative_count:
            sentiment = 'positive'
            score = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = 'negative'
            score = max(0.1, 0.5 - (negative_count - positive_count) * 0.1)
        else:
            sentiment = 'neutral'
            score = 0.5

        return {
            'sentiment': sentiment,
            'score': round(score, 2),
            'confidence': min(0.95, 0.6 + abs(positive_count - negative_count) * 0.1)
        }

    def get_market_sentiment_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Tổng hợp tâm lý thị trường từ tin tức
        """
        try:
            # Get recent news
            news = self.get_latest_news(limit=50)

            # Filter news from last N days
            cutoff_time = datetime.now() - timedelta(days=days)
            recent_news = [
                n for n in news
                if datetime.fromisoformat(n['timestamp']) > cutoff_time
            ]

            if not recent_news:
                return {
                    'overall_sentiment': 'neutral',
                    'sentiment_score': 0.5,
                    'total_news': 0,
                    'positive_ratio': 0,
                    'negative_ratio': 0,
                    'neutral_ratio': 0
                }

            # Count sentiments
            sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
            total_score = 0

            for news_item in recent_news:
                sentiment_data = news_item.get('sentiment', {})
                sentiment = sentiment_data.get('sentiment', 'neutral')
                score = sentiment_data.get('score', 0.5)

                sentiment_counts[sentiment] += 1
                total_score += score

            total = len(recent_news)
            avg_score = total_score / total if total > 0 else 0.5

            # Determine overall sentiment
            if avg_score > 0.6:
                overall = 'positive'
            elif avg_score < 0.4:
                overall = 'negative'
            else:
                overall = 'neutral'

            return {
                'overall_sentiment': overall,
                'sentiment_score': round(avg_score, 2),
                'total_news': total,
                'positive_ratio': round(sentiment_counts['positive'] / total * 100, 1) if total > 0 else 0,
                'negative_ratio': round(sentiment_counts['negative'] / total * 100, 1) if total > 0 else 0,
                'neutral_ratio': round(sentiment_counts['neutral'] / total * 100, 1) if total > 0 else 0,
                'period_days': days,
                'trending_topics': self._extract_trending_topics(recent_news)
            }

        except Exception as e:
            print(f"Error getting sentiment summary: {e}")
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.5,
                'total_news': 0,
                'positive_ratio': 0,
                'negative_ratio': 0,
                'neutral_ratio': 0,
                'period_days': days
            }

    def _extract_trending_topics(self, news_list: List[Dict]) -> List[str]:
        """Extract trending topics from news"""
        # Simple implementation - count categories
        category_counts = {}
        for news in news_list:
            category = news.get('category', 'Other')
            category_counts[category] = category_counts.get(category, 0) + 1

        # Sort by count
        sorted_topics = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)

        return [topic for topic, _ in sorted_topics[:5]]

    def search_news(
        self,
        query: str,
        limit: int = 20,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Tìm kiếm tin tức theo từ khóa
        """
        try:
            # Get all recent news
            all_news = self.get_latest_news(limit=100)

            # Filter by query
            query_lower = query.lower()
            filtered_news = [
                news for news in all_news
                if query_lower in news['title'].lower() or
                   query_lower in news.get('description', '').lower()
            ]

            # Filter by date
            cutoff_time = datetime.now() - timedelta(days=days)
            filtered_news = [
                news for news in filtered_news
                if datetime.fromisoformat(news['timestamp']) > cutoff_time
            ]

            return filtered_news[:limit]

        except Exception as e:
            print(f"Error searching news: {e}")
            return []
