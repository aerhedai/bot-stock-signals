"""
Technical Indicators for Cryptocurrency Analysis

Provides RSI, Moving Averages, Bollinger Bands, and other indicators.
"""

import logging
import numpy as np
import pandas as pd
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """Calculate technical indicators for crypto price data."""

    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> Optional[float]:
        """
        Calculate Relative Strength Index (RSI).

        Args:
            prices: Series of closing prices
            period: RSI period (default 14)

        Returns:
            Current RSI value or None if insufficient data
        """
        try:
            if len(prices) < period + 1:
                return None

            # Calculate price changes
            delta = prices.diff()

            # Separate gains and losses
            gains = delta.where(delta > 0, 0.0)
            losses = -delta.where(delta < 0, 0.0)

            # Calculate average gains and losses
            avg_gain = gains.rolling(window=period).mean()
            avg_loss = losses.rolling(window=period).mean()

            # Calculate RS and RSI
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

            return float(rsi.iloc[-1])

        except Exception as e:
            logger.error(f"Error calculating RSI: {e}")
            return None

    @staticmethod
    def calculate_ema(prices: pd.Series, period: int) -> Optional[float]:
        """
        Calculate Exponential Moving Average (EMA).

        Args:
            prices: Series of closing prices
            period: EMA period

        Returns:
            Current EMA value or None if insufficient data
        """
        try:
            if len(prices) < period:
                return None

            ema = prices.ewm(span=period, adjust=False).mean()
            return float(ema.iloc[-1])

        except Exception as e:
            logger.error(f"Error calculating EMA: {e}")
            return None

    @staticmethod
    def calculate_sma(prices: pd.Series, period: int) -> Optional[float]:
        """
        Calculate Simple Moving Average (SMA).

        Args:
            prices: Series of closing prices
            period: SMA period

        Returns:
            Current SMA value or None if insufficient data
        """
        try:
            if len(prices) < period:
                return None

            sma = prices.rolling(window=period).mean()
            return float(sma.iloc[-1])

        except Exception as e:
            logger.error(f"Error calculating SMA: {e}")
            return None

    @staticmethod
    def calculate_bollinger_bands(
        prices: pd.Series,
        period: int = 20,
        std_dev: int = 2
    ) -> Optional[Dict[str, float]]:
        """
        Calculate Bollinger Bands.

        Args:
            prices: Series of closing prices
            period: Moving average period
            std_dev: Number of standard deviations

        Returns:
            Dict with 'upper', 'middle', 'lower' bands or None
        """
        try:
            if len(prices) < period:
                return None

            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()

            upper = sma + (std * std_dev)
            lower = sma - (std * std_dev)

            return {
                'upper': float(upper.iloc[-1]),
                'middle': float(sma.iloc[-1]),
                'lower': float(lower.iloc[-1])
            }

        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands: {e}")
            return None

    @staticmethod
    def calculate_macd(
        prices: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Optional[Dict[str, float]]:
        """
        Calculate MACD (Moving Average Convergence Divergence).

        Args:
            prices: Series of closing prices
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period

        Returns:
            Dict with 'macd', 'signal', 'histogram' or None
        """
        try:
            if len(prices) < slow_period + signal_period:
                return None

            # Calculate EMAs
            ema_fast = prices.ewm(span=fast_period, adjust=False).mean()
            ema_slow = prices.ewm(span=slow_period, adjust=False).mean()

            # Calculate MACD line
            macd_line = ema_fast - ema_slow

            # Calculate signal line
            signal_line = macd_line.ewm(span=signal_period, adjust=False).mean()

            # Calculate histogram
            histogram = macd_line - signal_line

            return {
                'macd': float(macd_line.iloc[-1]),
                'signal': float(signal_line.iloc[-1]),
                'histogram': float(histogram.iloc[-1])
            }

        except Exception as e:
            logger.error(f"Error calculating MACD: {e}")
            return None

    @staticmethod
    def calculate_volume_sma(volumes: pd.Series, period: int = 20) -> Optional[float]:
        """
        Calculate average volume over period.

        Args:
            volumes: Series of volume data
            period: Period for average

        Returns:
            Average volume or None
        """
        try:
            if len(volumes) < period:
                return None

            avg_volume = volumes.rolling(window=period).mean()
            return float(avg_volume.iloc[-1])

        except Exception as e:
            logger.error(f"Error calculating volume SMA: {e}")
            return None

    @staticmethod
    def detect_golden_cross(
        prices: pd.Series,
        short_period: int = 50,
        long_period: int = 200
    ) -> bool:
        """
        Detect golden cross (short MA crosses above long MA).

        Args:
            prices: Series of closing prices
            short_period: Short MA period
            long_period: Long MA period

        Returns:
            True if golden cross detected
        """
        try:
            if len(prices) < long_period + 2:
                return False

            short_ma = prices.rolling(window=short_period).mean()
            long_ma = prices.rolling(window=long_period).mean()

            # Check if short MA crossed above long MA recently (within last 2 periods)
            current_cross = short_ma.iloc[-1] > long_ma.iloc[-1]
            previous_cross = short_ma.iloc[-2] < long_ma.iloc[-2]

            return current_cross and previous_cross

        except Exception as e:
            logger.error(f"Error detecting golden cross: {e}")
            return False

    @staticmethod
    def detect_death_cross(
        prices: pd.Series,
        short_period: int = 50,
        long_period: int = 200
    ) -> bool:
        """
        Detect death cross (short MA crosses below long MA).

        Args:
            prices: Series of closing prices
            short_period: Short MA period
            long_period: Long MA period

        Returns:
            True if death cross detected
        """
        try:
            if len(prices) < long_period + 2:
                return False

            short_ma = prices.rolling(window=short_period).mean()
            long_ma = prices.rolling(window=long_period).mean()

            # Check if short MA crossed below long MA recently
            current_cross = short_ma.iloc[-1] < long_ma.iloc[-1]
            previous_cross = short_ma.iloc[-2] > long_ma.iloc[-2]

            return current_cross and previous_cross

        except Exception as e:
            logger.error(f"Error detecting death cross: {e}")
            return False
