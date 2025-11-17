"""
Module nhận dạng các mô hình nến Nhật (Japanese Candlestick Patterns)
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any


class CandlestickPatternDetector:
    """Class nhận dạng các mô hình nến Nhật"""

    def __init__(self, df: pd.DataFrame):
        """
        Khởi tạo với DataFrame chứa dữ liệu giá

        Args:
            df: DataFrame với các cột: open, high, low, close, volume
        """
        self.df = df.copy()

        # Chuẩn hóa tên cột
        column_mapping = {
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }
        self.df.rename(columns=column_mapping, inplace=True)

        # Tính các giá trị cần thiết
        self.df['body'] = abs(self.df['close'] - self.df['open'])
        self.df['upper_shadow'] = self.df['high'] - self.df[['open', 'close']].max(axis=1)
        self.df['lower_shadow'] = self.df[['open', 'close']].min(axis=1) - self.df['low']
        self.df['is_bullish'] = self.df['close'] > self.df['open']
        self.df['is_bearish'] = self.df['close'] < self.df['open']
        self.df['range'] = self.df['high'] - self.df['low']

    def detect_doji(self, threshold: float = 0.1) -> pd.Series:
        """
        Nhận dạng mô hình Doji
        Đặc điểm: Body rất nhỏ (open ≈ close)

        Args:
            threshold: Ngưỡng body/range tối đa để coi là Doji

        Returns:
            Series boolean đánh dấu vị trí có Doji
        """
        body_ratio = self.df['body'] / self.df['range']
        return body_ratio < threshold

    def detect_hammer(self, body_threshold: float = 0.3, shadow_ratio: float = 2.0) -> pd.Series:
        """
        Nhận dạng mô hình Hammer (Búa)
        Đặc điểm: Body nhỏ ở đỉnh, lower shadow dài gấp ít nhất 2 lần body

        Args:
            body_threshold: Tỷ lệ body/range tối đa
            shadow_ratio: Tỷ lệ lower_shadow/body tối thiểu

        Returns:
            Series boolean đánh dấu vị trí có Hammer
        """
        body_ratio = self.df['body'] / self.df['range']
        lower_shadow_ratio = self.df['lower_shadow'] / (self.df['body'] + 0.0001)  # Tránh chia cho 0

        return (
            (body_ratio < body_threshold) &
            (lower_shadow_ratio > shadow_ratio) &
            (self.df['upper_shadow'] < self.df['body'])
        )

    def detect_inverted_hammer(self, body_threshold: float = 0.3, shadow_ratio: float = 2.0) -> pd.Series:
        """
        Nhận dạng mô hình Inverted Hammer (Búa ngược)
        Đặc điểm: Body nhỏ ở đáy, upper shadow dài gấp ít nhất 2 lần body

        Args:
            body_threshold: Tỷ lệ body/range tối đa
            shadow_ratio: Tỷ lệ upper_shadow/body tối thiểu

        Returns:
            Series boolean đánh dấu vị trí có Inverted Hammer
        """
        body_ratio = self.df['body'] / self.df['range']
        upper_shadow_ratio = self.df['upper_shadow'] / (self.df['body'] + 0.0001)

        return (
            (body_ratio < body_threshold) &
            (upper_shadow_ratio > shadow_ratio) &
            (self.df['lower_shadow'] < self.df['body'])
        )

    def detect_shooting_star(self, body_threshold: float = 0.3, shadow_ratio: float = 2.0) -> pd.Series:
        """
        Nhận dạng mô hình Shooting Star (Sao băng)
        Giống Inverted Hammer nhưng xuất hiện sau uptrend

        Args:
            body_threshold: Tỷ lệ body/range tối đa
            shadow_ratio: Tỷ lệ upper_shadow/body tối thiểu

        Returns:
            Series boolean đánh dấu vị trí có Shooting Star
        """
        return self.detect_inverted_hammer(body_threshold, shadow_ratio)

    def detect_engulfing_bullish(self) -> pd.Series:
        """
        Nhận dạng mô hình Bullish Engulfing (Nhấn chìm tăng)
        Đặc điểm: Nến tăng bao phủ hoàn toàn nến giảm trước đó

        Returns:
            Series boolean đánh dấu vị trí có Bullish Engulfing
        """
        result = pd.Series([False] * len(self.df), index=self.df.index)

        for i in range(1, len(self.df)):
            prev = self.df.iloc[i-1]
            curr = self.df.iloc[i]

            # Nến trước là bearish, nến hiện tại là bullish
            # Nến hiện tại bao phủ hoàn toàn nến trước
            if (prev['is_bearish'] and curr['is_bullish'] and
                curr['open'] < prev['close'] and curr['close'] > prev['open']):
                result.iloc[i] = True

        return result

    def detect_engulfing_bearish(self) -> pd.Series:
        """
        Nhận dạng mô hình Bearish Engulfing (Nhấn chìm giảm)
        Đặc điểm: Nến giảm bao phủ hoàn toàn nến tăng trước đó

        Returns:
            Series boolean đánh dấu vị trí có Bearish Engulfing
        """
        result = pd.Series([False] * len(self.df), index=self.df.index)

        for i in range(1, len(self.df)):
            prev = self.df.iloc[i-1]
            curr = self.df.iloc[i]

            # Nến trước là bullish, nến hiện tại là bearish
            # Nến hiện tại bao phủ hoàn toàn nến trước
            if (prev['is_bullish'] and curr['is_bearish'] and
                curr['open'] > prev['close'] and curr['close'] < prev['open']):
                result.iloc[i] = True

        return result

    def detect_morning_star(self) -> pd.Series:
        """
        Nhận dạng mô hình Morning Star (Sao mai)
        Đặc điểm: 3 nến - bearish, doji/small body, bullish

        Returns:
            Series boolean đánh dấu vị trí có Morning Star
        """
        result = pd.Series([False] * len(self.df), index=self.df.index)

        for i in range(2, len(self.df)):
            candle1 = self.df.iloc[i-2]
            candle2 = self.df.iloc[i-1]
            candle3 = self.df.iloc[i]

            # Nến 1: Bearish với body lớn
            # Nến 2: Body nhỏ (doji hoặc gần doji)
            # Nến 3: Bullish với body lớn
            if (candle1['is_bearish'] and
                candle1['body'] > candle1['range'] * 0.5 and
                candle2['body'] < candle2['range'] * 0.3 and
                candle3['is_bullish'] and
                candle3['body'] > candle3['range'] * 0.5 and
                candle3['close'] > (candle1['open'] + candle1['close']) / 2):
                result.iloc[i] = True

        return result

    def detect_evening_star(self) -> pd.Series:
        """
        Nhận dạng mô hình Evening Star (Sao hôm)
        Đặc điểm: 3 nến - bullish, doji/small body, bearish

        Returns:
            Series boolean đánh dấu vị trí có Evening Star
        """
        result = pd.Series([False] * len(self.df), index=self.df.index)

        for i in range(2, len(self.df)):
            candle1 = self.df.iloc[i-2]
            candle2 = self.df.iloc[i-1]
            candle3 = self.df.iloc[i]

            # Nến 1: Bullish với body lớn
            # Nến 2: Body nhỏ (doji hoặc gần doji)
            # Nến 3: Bearish với body lớn
            if (candle1['is_bullish'] and
                candle1['body'] > candle1['range'] * 0.5 and
                candle2['body'] < candle2['range'] * 0.3 and
                candle3['is_bearish'] and
                candle3['body'] > candle3['range'] * 0.5 and
                candle3['close'] < (candle1['open'] + candle1['close']) / 2):
                result.iloc[i] = True

        return result

    def detect_three_white_soldiers(self) -> pd.Series:
        """
        Nhận dạng mô hình Three White Soldiers (Ba người lính)
        Đặc điểm: 3 nến tăng liên tiếp, mỗi nến cao hơn nến trước

        Returns:
            Series boolean đánh dấu vị trí có Three White Soldiers
        """
        result = pd.Series([False] * len(self.df), index=self.df.index)

        for i in range(2, len(self.df)):
            c1 = self.df.iloc[i-2]
            c2 = self.df.iloc[i-1]
            c3 = self.df.iloc[i]

            # 3 nến tăng liên tiếp
            if (c1['is_bullish'] and c2['is_bullish'] and c3['is_bullish'] and
                c2['close'] > c1['close'] and c3['close'] > c2['close'] and
                c2['open'] > c1['open'] and c3['open'] > c2['open']):
                result.iloc[i] = True

        return result

    def detect_three_black_crows(self) -> pd.Series:
        """
        Nhận dạng mô hình Three Black Crows (Ba con quạ)
        Đặc điểm: 3 nến giảm liên tiếp, mỗi nến thấp hơn nến trước

        Returns:
            Series boolean đánh dấu vị trí có Three Black Crows
        """
        result = pd.Series([False] * len(self.df), index=self.df.index)

        for i in range(2, len(self.df)):
            c1 = self.df.iloc[i-2]
            c2 = self.df.iloc[i-1]
            c3 = self.df.iloc[i]

            # 3 nến giảm liên tiếp
            if (c1['is_bearish'] and c2['is_bearish'] and c3['is_bearish'] and
                c2['close'] < c1['close'] and c3['close'] < c2['close'] and
                c2['open'] < c1['open'] and c3['open'] < c2['open']):
                result.iloc[i] = True

        return result

    def detect_harami_bullish(self) -> pd.Series:
        """
        Nhận dạng mô hình Bullish Harami (Mang thai tăng)
        Đặc điểm: Nến tăng nhỏ nằm trong body của nến giảm lớn trước đó

        Returns:
            Series boolean đánh dấu vị trí có Bullish Harami
        """
        result = pd.Series([False] * len(self.df), index=self.df.index)

        for i in range(1, len(self.df)):
            prev = self.df.iloc[i-1]
            curr = self.df.iloc[i]

            # Nến trước bearish lớn, nến hiện tại bullish nhỏ nằm trong body nến trước
            if (prev['is_bearish'] and curr['is_bullish'] and
                curr['open'] > prev['close'] and curr['close'] < prev['open'] and
                curr['body'] < prev['body'] * 0.5):
                result.iloc[i] = True

        return result

    def detect_harami_bearish(self) -> pd.Series:
        """
        Nhận dạng mô hình Bearish Harami (Mang thai giảm)
        Đặc điểm: Nến giảm nhỏ nằm trong body của nến tăng lớn trước đó

        Returns:
            Series boolean đánh dấu vị trí có Bearish Harami
        """
        result = pd.Series([False] * len(self.df), index=self.df.index)

        for i in range(1, len(self.df)):
            prev = self.df.iloc[i-1]
            curr = self.df.iloc[i]

            # Nến trước bullish lớn, nến hiện tại bearish nhỏ nằm trong body nến trước
            if (prev['is_bullish'] and curr['is_bearish'] and
                curr['open'] < prev['close'] and curr['close'] > prev['open'] and
                curr['body'] < prev['body'] * 0.5):
                result.iloc[i] = True

        return result

    def detect_all_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Nhận dạng tất cả các mô hình nến Nhật

        Returns:
            Dictionary chứa tất cả các mô hình được phát hiện
        """
        patterns = {
            'Doji': self.detect_doji(),
            'Hammer': self.detect_hammer(),
            'Inverted_Hammer': self.detect_inverted_hammer(),
            'Shooting_Star': self.detect_shooting_star(),
            'Bullish_Engulfing': self.detect_engulfing_bullish(),
            'Bearish_Engulfing': self.detect_engulfing_bearish(),
            'Morning_Star': self.detect_morning_star(),
            'Evening_Star': self.detect_evening_star(),
            'Three_White_Soldiers': self.detect_three_white_soldiers(),
            'Three_Black_Crows': self.detect_three_black_crows(),
            'Bullish_Harami': self.detect_harami_bullish(),
            'Bearish_Harami': self.detect_harami_bearish()
        }

        # Chuyển đổi sang format dễ đọc
        result = {}
        for pattern_name, series in patterns.items():
            detected_indices = series[series].index.tolist()
            detected_patterns = []

            for idx in detected_indices:
                try:
                    # Try to get date from 'time' column first
                    if 'time' in self.df.columns:
                        date_val = self.df.iloc[idx]['time']
                        if hasattr(date_val, 'strftime'):
                            date_str = date_val.strftime('%Y-%m-%d')
                        else:
                            date_str = str(date_val)
                    # Then try from index
                    else:
                        date_val = self.df.index[idx]
                        if hasattr(date_val, 'strftime'):
                            date_str = date_val.strftime('%Y-%m-%d')
                        else:
                            date_str = str(date_val)
                except:
                    date_str = str(idx)

                detected_patterns.append({
                    'date': date_str,
                    'index': int(idx),
                    'close': float(self.df.iloc[idx]['close']),
                    'pattern_type': pattern_name
                })

            result[pattern_name] = detected_patterns

        # Thêm summary
        result['summary'] = {
            'total_patterns': sum(len(v) for v in result.values() if isinstance(v, list)),
            'patterns_found': [k for k, v in result.items() if isinstance(v, list) and len(v) > 0]
        }

        return result

    def get_latest_patterns(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Lấy n mô hình gần nhất

        Args:
            n: Số lượng mô hình gần nhất cần lấy

        Returns:
            Danh sách các mô hình gần nhất
        """
        all_patterns = self.detect_all_patterns()
        latest = []

        for pattern_name, detections in all_patterns.items():
            if pattern_name != 'summary' and isinstance(detections, list):
                for detection in detections:
                    latest.append({
                        **detection,
                        'pattern_name': pattern_name
                    })

        # Sắp xếp theo index giảm dần
        latest.sort(key=lambda x: x['index'], reverse=True)

        return latest[:n]
