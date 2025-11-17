"""
Module tính toán các chỉ số kỹ thuật (Technical Indicators)
"""
import pandas as pd
import numpy as np
from ta.trend import SMAIndicator, EMAIndicator, MACD, IchimokuIndicator, PSARIndicator, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, MFIIndicator, ChaikinMoneyFlowIndicator, AccDistIndexIndicator
from typing import Dict, Any


class TechnicalAnalyzer:
    """Class phân tích kỹ thuật"""

    def __init__(self, df: pd.DataFrame):
        """
        Khởi tạo với DataFrame chứa dữ liệu giá

        Args:
            df: DataFrame với các cột: time/date, open, high, low, close, volume
        """
        self.df = df.copy()

        # Chuẩn hóa tên cột
        column_mapping = {
            'time': 'date',
            'Time': 'date',
            'Date': 'date',
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }
        self.df.rename(columns=column_mapping, inplace=True)

        # Đảm bảo có đủ các cột cần thiết
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in self.df.columns:
                raise ValueError(f"Missing required column: {col}")

    def calculate_sma(self, periods: list = [20, 50, 100, 200]) -> Dict[str, Any]:
        """
        Tính Simple Moving Average

        Args:
            periods: Danh sách các kỳ để tính SMA

        Returns:
            Dictionary chứa SMA cho các kỳ khác nhau
        """
        result = {}
        for period in periods:
            if len(self.df) >= period:
                sma = SMAIndicator(close=self.df['close'], window=period)
                result[f'SMA_{period}'] = sma.sma_indicator().fillna(0).tolist()
        return result

    def calculate_ema(self, periods: list = [12, 26, 50, 200]) -> Dict[str, Any]:
        """
        Tính Exponential Moving Average

        Args:
            periods: Danh sách các kỳ để tính EMA

        Returns:
            Dictionary chứa EMA cho các kỳ khác nhau
        """
        result = {}
        for period in periods:
            if len(self.df) >= period:
                ema = EMAIndicator(close=self.df['close'], window=period)
                result[f'EMA_{period}'] = ema.ema_indicator().fillna(0).tolist()
        return result

    def calculate_macd(self, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, Any]:
        """
        Tính MACD (Moving Average Convergence Divergence)

        Args:
            fast: Kỳ EMA nhanh
            slow: Kỳ EMA chậm
            signal: Kỳ signal line

        Returns:
            Dictionary chứa MACD, signal và histogram
        """
        if len(self.df) >= slow:
            macd = MACD(close=self.df['close'], window_fast=fast, window_slow=slow, window_sign=signal)
            return {
                'MACD': macd.macd().fillna(0).tolist(),
                'Signal': macd.macd_signal().fillna(0).tolist(),
                'Histogram': macd.macd_diff().fillna(0).tolist()
            }
        return {}

    def calculate_rsi(self, period: int = 14) -> Dict[str, Any]:
        """
        Tính RSI (Relative Strength Index)

        Args:
            period: Kỳ tính RSI

        Returns:
            Dictionary chứa giá trị RSI
        """
        if len(self.df) >= period:
            rsi = RSIIndicator(close=self.df['close'], window=period)
            return {
                'RSI': rsi.rsi().fillna(50).tolist(),
                'period': period
            }
        return {}

    def calculate_bollinger_bands(self, period: int = 20, std_dev: int = 2) -> Dict[str, Any]:
        """
        Tính Bollinger Bands

        Args:
            period: Kỳ tính MA
            std_dev: Số độ lệch chuẩn

        Returns:
            Dictionary chứa upper, middle, lower bands
        """
        if len(self.df) >= period:
            bb = BollingerBands(close=self.df['close'], window=period, window_dev=std_dev)
            return {
                'Upper': bb.bollinger_hband().fillna(0).tolist(),
                'Middle': bb.bollinger_mavg().fillna(0).tolist(),
                'Lower': bb.bollinger_lband().fillna(0).tolist(),
                'BandWidth': bb.bollinger_wband().fillna(0).tolist(),
                'PercentB': bb.bollinger_pband().fillna(0).tolist()
            }
        return {}

    def calculate_atr(self, period: int = 14) -> Dict[str, Any]:
        """
        Tính ATR (Average True Range)

        Args:
            period: Kỳ tính ATR

        Returns:
            Dictionary chứa giá trị ATR
        """
        if len(self.df) >= period:
            atr = AverageTrueRange(high=self.df['high'], low=self.df['low'],
                                   close=self.df['close'], window=period)
            return {
                'ATR': atr.average_true_range().fillna(0).tolist(),
                'period': period
            }
        return {}

    def calculate_obv(self) -> Dict[str, Any]:
        """
        Tính OBV (On Balance Volume)

        Returns:
            Dictionary chứa giá trị OBV
        """
        obv = OnBalanceVolumeIndicator(close=self.df['close'], volume=self.df['volume'])
        return {
            'OBV': obv.on_balance_volume().fillna(0).tolist()
        }

    def calculate_ichimoku(self, conversion: int = 9, base: int = 26,
                          span_b: int = 52, displacement: int = 26) -> Dict[str, Any]:
        """
        Tính Ichimoku Cloud

        Args:
            conversion: Kỳ Tenkan-sen
            base: Kỳ Kijun-sen
            span_b: Kỳ Senkou Span B
            displacement: Kỳ dịch chuyển

        Returns:
            Dictionary chứa các đường Ichimoku
        """
        if len(self.df) >= span_b:
            ichimoku = IchimokuIndicator(high=self.df['high'], low=self.df['low'],
                                        window1=conversion, window2=base, window3=span_b)
            return {
                'Tenkan_sen': ichimoku.ichimoku_conversion_line().fillna(0).tolist(),
                'Kijun_sen': ichimoku.ichimoku_base_line().fillna(0).tolist(),
                'Senkou_span_a': ichimoku.ichimoku_a().fillna(0).tolist(),
                'Senkou_span_b': ichimoku.ichimoku_b().fillna(0).tolist()
            }
        return {}

    def calculate_psar(self, step: float = 0.02, max_step: float = 0.2) -> Dict[str, Any]:
        """
        Tính Parabolic SAR

        Args:
            step: Bước tăng
            max_step: Bước tăng tối đa

        Returns:
            Dictionary chứa giá trị PSAR
        """
        if len(self.df) >= 2:
            psar = PSARIndicator(high=self.df['high'], low=self.df['low'],
                                close=self.df['close'], step=step, max_step=max_step)
            return {
                'PSAR': psar.psar().fillna(0).tolist(),
                'PSAR_up': psar.psar_up().fillna(0).tolist(),
                'PSAR_down': psar.psar_down().fillna(0).tolist()
            }
        return {}

    def calculate_mfi(self, period: int = 14) -> Dict[str, Any]:
        """
        Tính MFI (Money Flow Index)

        Args:
            period: Kỳ tính MFI

        Returns:
            Dictionary chứa giá trị MFI
        """
        if len(self.df) >= period:
            mfi = MFIIndicator(high=self.df['high'], low=self.df['low'],
                              close=self.df['close'], volume=self.df['volume'],
                              window=period)
            return {
                'MFI': mfi.money_flow_index().fillna(50).tolist(),
                'period': period
            }
        return {}

    def calculate_ad(self) -> Dict[str, Any]:
        """
        Tính A/D (Accumulation/Distribution)

        Returns:
            Dictionary chứa giá trị A/D
        """
        ad = AccDistIndexIndicator(high=self.df['high'], low=self.df['low'],
                                   close=self.df['close'], volume=self.df['volume'])
        return {
            'AD': ad.acc_dist_index().fillna(0).tolist()
        }

    def calculate_cmf(self, period: int = 20) -> Dict[str, Any]:
        """
        Tính CMF (Chaikin Money Flow)

        Args:
            period: Kỳ tính CMF

        Returns:
            Dictionary chứa giá trị CMF
        """
        if len(self.df) >= period:
            cmf = ChaikinMoneyFlowIndicator(high=self.df['high'], low=self.df['low'],
                                           close=self.df['close'], volume=self.df['volume'],
                                           window=period)
            return {
                'CMF': cmf.chaikin_money_flow().fillna(0).tolist(),
                'period': period
            }
        return {}

    def calculate_adl(self) -> Dict[str, Any]:
        """
        Tính ADL (Advance/Decline Line)
        Đơn giản hóa: Tính tích lũy của sự thay đổi giá

        Returns:
            Dictionary chứa giá trị ADL
        """
        price_change = self.df['close'].diff()
        adl = price_change.cumsum()
        return {
            'ADL': adl.fillna(0).tolist()
        }

    def calculate_all_indicators(self) -> Dict[str, Any]:
        """
        Tính toán tất cả các chỉ số kỹ thuật

        Returns:
            Dictionary chứa tất cả các chỉ số
        """
        return {
            'SMA': self.calculate_sma(),
            'EMA': self.calculate_ema(),
            'MACD': self.calculate_macd(),
            'RSI': self.calculate_rsi(),
            'BB': self.calculate_bollinger_bands(),
            'ATR': self.calculate_atr(),
            'OBV': self.calculate_obv(),
            'Ichimoku': self.calculate_ichimoku(),
            'PSAR': self.calculate_psar(),
            'MFI': self.calculate_mfi(),
            'AD': self.calculate_ad(),
            'CMF': self.calculate_cmf(),
            'ADL': self.calculate_adl()
        }
