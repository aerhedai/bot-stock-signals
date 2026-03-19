"""
Cryptocurrency Valuation Strategies

Methods to identify undervalued cryptocurrencies using various valuation approaches.
Similar to stock_sniper strategies but adapted for crypto markets.
"""

import logging
import numpy as np
import pandas as pd
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ValuationResult:
    """Result from a valuation method."""
    method_name: str
    is_undervalued: bool
    score: float  # 0-100, higher = more undervalued
    current_price: float
    fair_value_estimate: Optional[float] = None
    discount_percentage: Optional[float] = None
    confidence: str = "medium"  # low, medium, high
    details: Dict[str, Any] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}


class CryptoValuation:
    """
    Cryptocurrency valuation strategies to identify undervalued assets.

    Methods:
    1. Historical Z-Score: Find cryptos trading below historical average
    2. Volume-Weighted Fair Value: Use volume trends to estimate fair value
    3. Relative Strength: Compare to BTC/ETH performance
    4. Mean Reversion: Identify oversold conditions vs historical ranges
    """

    def __init__(self):
        """Initialise valuation calculator."""
        logger.info("CryptoValuation initialised")

    def method_1_historical_zscore(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        lookback_days: int = 180,
        threshold: float = -1.5
    ) -> Optional[ValuationResult]:
        """
        Method 1: Historical Z-Score Valuation

        Find cryptos trading significantly below their historical average price.
        A negative Z-score indicates undervaluation.

        Args:
            symbol: Crypto symbol
            price_data: Historical price data
            lookback_days: Days of history to analyse
            threshold: Z-score threshold (e.g., -1.5 = 1.5 std devs below mean)

        Returns:
            ValuationResult or None
        """
        try:
            if len(price_data) < lookback_days:
                logger.debug(f"{symbol}: Insufficient data for Z-score ({len(price_data)} < {lookback_days})")
                return None

            # Get recent data
            recent_data = price_data.tail(lookback_days)
            prices = recent_data['Close']

            current_price = float(prices.iloc[-1])
            mean_price = float(prices.mean())
            std_price = float(prices.std())

            if std_price == 0:
                logger.debug(f"{symbol}: Zero standard deviation")
                return None

            # Calculate Z-score
            zscore = (current_price - mean_price) / std_price

            # Check if undervalued (negative Z-score)
            is_undervalued = zscore <= threshold

            if not is_undervalued:
                return None

            # Calculate discount percentage
            discount = ((mean_price - current_price) / mean_price) * 100

            # Score: 0-100 based on how far below mean (more negative = higher score)
            # -1.5 Z = 50, -2.0 Z = 70, -3.0 Z = 100
            score = min(100, max(0, (abs(zscore) - 1.0) * 35))

            # Confidence based on data consistency
            confidence = "high" if len(recent_data) >= lookback_days else "medium"

            return ValuationResult(
                method_name="Historical Z-Score",
                is_undervalued=True,
                score=score,
                current_price=current_price,
                fair_value_estimate=mean_price,
                discount_percentage=discount,
                confidence=confidence,
                details={
                    'zscore': zscore,
                    'mean_price': mean_price,
                    'std_dev': std_price,
                    'lookback_days': lookback_days,
                    'threshold': threshold
                }
            )

        except Exception as e:
            logger.error(f"Error in Z-score valuation for {symbol}: {e}")
            return None

    def method_2_volume_fair_value(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        volume_period: int = 90,
        price_volume_ratio_threshold: float = 0.7
    ) -> Optional[ValuationResult]:
        """
        Method 2: Volume-Weighted Fair Value

        Estimate fair value based on volume-weighted average price and
        detect when current price deviates significantly.

        Args:
            symbol: Crypto symbol
            price_data: Historical price data
            volume_period: Days to calculate VWAP
            price_volume_ratio_threshold: Discount threshold

        Returns:
            ValuationResult or None
        """
        try:
            if len(price_data) < volume_period:
                logger.debug(f"{symbol}: Insufficient data for volume analysis")
                return None

            recent_data = price_data.tail(volume_period)

            # Calculate Volume-Weighted Average Price (VWAP)
            typical_price = (recent_data['High'] + recent_data['Low'] + recent_data['Close']) / 3
            vwap = (typical_price * recent_data['Volume']).sum() / recent_data['Volume'].sum()

            current_price = float(recent_data['Close'].iloc[-1])

            # Calculate discount
            discount = ((vwap - current_price) / vwap) * 100

            # Check if undervalued (current price significantly below VWAP)
            is_undervalued = discount >= (price_volume_ratio_threshold * 100)

            if not is_undervalued:
                return None

            # Score based on discount percentage
            score = min(100, max(0, discount * 2))

            return ValuationResult(
                method_name="Volume-Weighted Fair Value",
                is_undervalued=True,
                score=score,
                current_price=current_price,
                fair_value_estimate=float(vwap),
                discount_percentage=discount,
                confidence="medium",
                details={
                    'vwap': float(vwap),
                    'volume_period': volume_period,
                    'avg_volume': float(recent_data['Volume'].mean())
                }
            )

        except Exception as e:
            logger.error(f"Error in volume fair value for {symbol}: {e}")
            return None

    def method_3_relative_underperformance(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        btc_data: pd.DataFrame,
        lookback_days: int = 90,
        underperformance_threshold: float = -15.0
    ) -> Optional[ValuationResult]:
        """
        Method 3: Relative Strength vs Bitcoin

        Find cryptos that have significantly underperformed Bitcoin,
        indicating potential value opportunities.

        Args:
            symbol: Crypto symbol
            price_data: Crypto price data
            btc_data: Bitcoin price data
            lookback_days: Comparison period
            underperformance_threshold: Threshold for underperformance (%)

        Returns:
            ValuationResult or None
        """
        try:
            if len(price_data) < lookback_days or len(btc_data) < lookback_days:
                logger.debug(f"{symbol}: Insufficient data for relative strength")
                return None

            # Calculate returns
            crypto_start = float(price_data['Close'].iloc[-lookback_days])
            crypto_current = float(price_data['Close'].iloc[-1])
            crypto_return = ((crypto_current - crypto_start) / crypto_start) * 100

            btc_start = float(btc_data['Close'].iloc[-lookback_days])
            btc_current = float(btc_data['Close'].iloc[-1])
            btc_return = ((btc_current - btc_start) / btc_start) * 100

            # Calculate relative underperformance
            relative_performance = crypto_return - btc_return

            # Check if significantly underperforming BTC
            is_undervalued = relative_performance <= underperformance_threshold

            if not is_undervalued:
                return None

            # Score based on degree of underperformance
            score = min(100, max(0, (abs(relative_performance) - 10) * 3))

            # Estimate fair value assuming crypto should track BTC
            implied_price = crypto_start * (1 + btc_return / 100)
            discount = ((implied_price - crypto_current) / implied_price) * 100

            return ValuationResult(
                method_name="Relative Underperformance vs BTC",
                is_undervalued=True,
                score=score,
                current_price=crypto_current,
                fair_value_estimate=float(implied_price),
                discount_percentage=discount,
                confidence="medium",
                details={
                    'crypto_return': crypto_return,
                    'btc_return': btc_return,
                    'relative_performance': relative_performance,
                    'lookback_days': lookback_days
                }
            )

        except Exception as e:
            logger.error(f"Error in relative underperformance for {symbol}: {e}")
            return None

    def method_4_bollinger_mean_reversion(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        bb_period: int = 50,
        bb_std: float = 2.0,
        min_deviation: float = 0.10
    ) -> Optional[ValuationResult]:
        """
        Method 4: Bollinger Band Mean Reversion

        Identify cryptos trading significantly below their Bollinger Band lower bound,
        indicating potential mean reversion opportunity.

        Args:
            symbol: Crypto symbol
            price_data: Historical price data
            bb_period: Bollinger Band period
            bb_std: Standard deviation multiplier
            min_deviation: Minimum % below lower band

        Returns:
            ValuationResult or None
        """
        try:
            if len(price_data) < bb_period + 10:
                logger.debug(f"{symbol}: Insufficient data for Bollinger Bands")
                return None

            prices = price_data['Close']

            # Calculate Bollinger Bands
            sma = prices.rolling(window=bb_period).mean()
            std = prices.rolling(window=bb_period).std()

            upper_band = sma + (std * bb_std)
            lower_band = sma - (std * bb_std)

            current_price = float(prices.iloc[-1])
            current_lower = float(lower_band.iloc[-1])
            current_sma = float(sma.iloc[-1])

            # Calculate how far below lower band
            deviation_from_lower = ((current_lower - current_price) / current_lower) * 100

            # Check if significantly below lower band
            is_undervalued = deviation_from_lower >= (min_deviation * 100)

            if not is_undervalued:
                return None

            # Score based on deviation
            score = min(100, max(0, deviation_from_lower * 4))

            # Estimate fair value as SMA
            discount = ((current_sma - current_price) / current_sma) * 100

            return ValuationResult(
                method_name="Bollinger Mean Reversion",
                is_undervalued=True,
                score=score,
                current_price=current_price,
                fair_value_estimate=current_sma,
                discount_percentage=discount,
                confidence="medium",
                details={
                    'lower_band': current_lower,
                    'sma': current_sma,
                    'upper_band': float(upper_band.iloc[-1]),
                    'deviation_from_lower': deviation_from_lower,
                    'bb_period': bb_period
                }
            )

        except Exception as e:
            logger.error(f"Error in Bollinger mean reversion for {symbol}: {e}")
            return None

    def analyze_all_methods(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        btc_data: Optional[pd.DataFrame] = None
    ) -> List[ValuationResult]:
        """
        Run all valuation methods and return results.

        Args:
            symbol: Crypto symbol
            price_data: Historical price data
            btc_data: Bitcoin price data for relative strength

        Returns:
            List of ValuationResults (only undervalued ones)
        """
        results = []

        # Method 1: Historical Z-Score (6 months)
        result = self.method_1_historical_zscore(symbol, price_data, lookback_days=180)
        if result:
            results.append(result)

        # Method 2: Volume Fair Value (3 months)
        result = self.method_2_volume_fair_value(symbol, price_data, volume_period=90)
        if result:
            results.append(result)

        # Method 3: Relative vs BTC (if BTC data provided)
        if btc_data is not None and len(btc_data) > 0:
            result = self.method_3_relative_underperformance(symbol, price_data, btc_data)
            if result:
                results.append(result)

        # Method 4: Bollinger Mean Reversion
        result = self.method_4_bollinger_mean_reversion(symbol, price_data)
        if result:
            results.append(result)

        return results

    def get_best_valuation(self, results: List[ValuationResult]) -> Optional[ValuationResult]:
        """
        Get the strongest valuation signal from multiple results.

        Args:
            results: List of valuation results

        Returns:
            Best valuation result or None
        """
        if not results:
            return None

        # Sort by score (highest first)
        sorted_results = sorted(results, key=lambda r: r.score, reverse=True)

        return sorted_results[0]
