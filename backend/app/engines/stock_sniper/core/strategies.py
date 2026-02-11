"""
Valuation Strategies Module

Implements three distinct mathematical strategies for identifying undervalued stocks:
1. Graham Number (Deep Value) - Long-Term Conviction Picks (3-12 months)
2. Z-Score (Panic Reversion) - Short-Term Momentum (1-5 trading days)
3. Linear Regression (Trend Deviation) - Swing Trade Candidates (1-4 weeks)
"""

import logging
import yfinance as yf
import pandas as pd
import numpy as np
from enum import Enum
from sklearn.linear_model import LinearRegression
from typing import Tuple, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from app.engines.stock_sniper.config import settings

logger = logging.getLogger(__name__)


class TimeHorizon(Enum):
    """Time horizon categories for investment strategies."""
    SHORT_TERM = "Short-Term Momentum (1-5 days)"
    SWING_TRADE = "Swing Trade Candidates (1-4 weeks)"
    LONG_TERM = "Long-Term Conviction Picks (3-12 months)"


@dataclass
class StrategyResult:
    """Result from a valuation strategy."""
    is_undervalued: bool
    method_name: str
    reason: str
    score: float  # 0-100 confidence score
    current_price: float
    time_horizon: TimeHorizon
    target_price: Optional[float] = None
    details: Dict[str, Any] = None


class GrahamNumberStrategy:
    """
    Method 1: Deep Value (Graham Number)

    Formula: Graham Price = √(22.5 × EPS × Book Value Per Share)
    Condition: Current Price < 0.80 × Graham Price (20% discount)

    This strategy identifies stocks trading significantly below their
    intrinsic value based on earnings and book value.
    """

    def __init__(self):
        self.discount_threshold = settings.GRAHAM_DISCOUNT_THRESHOLD
        self.min_eps = settings.GRAHAM_MIN_EPS
        self.min_book_value = settings.GRAHAM_MIN_BOOK_VALUE

    def evaluate(self, ticker: str) -> Optional[StrategyResult]:
        """
        Evaluate stock using Graham Number method.

        Args:
            ticker: Stock ticker symbol

        Returns:
            StrategyResult or None if evaluation fails
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Get required data
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            eps = info.get('trailingEps')
            book_value = info.get('bookValue')

            if not current_price:
                logger.debug(f"{ticker}: No price data")
                return None

            if not eps or eps < self.min_eps:
                logger.debug(f"{ticker}: Invalid EPS: {eps}")
                return None

            if not book_value or book_value < self.min_book_value:
                logger.debug(f"{ticker}: Invalid book value: {book_value}")
                return None

            # Calculate Graham Number
            graham_price = np.sqrt(22.5 * eps * book_value)
            threshold_price = graham_price * self.discount_threshold

            # Check if undervalued
            is_undervalued = current_price < threshold_price

            # Calculate discount percentage
            discount_pct = ((graham_price - current_price) / graham_price) * 100

            # Calculate confidence score (0-100)
            # More discount = higher confidence
            if is_undervalued:
                score = min(100, 50 + discount_pct * 2)
            else:
                score = max(0, 50 - abs(discount_pct))

            reason = (
                f"Current ${current_price:.2f} vs "
                f"Graham ${graham_price:.2f} "
                f"({'BELOW' if is_undervalued else 'ABOVE'} threshold ${threshold_price:.2f}, "
                f"{discount_pct:+.1f}% discount)"
            )

            return StrategyResult(
                is_undervalued=is_undervalued,
                method_name="Graham Number",
                reason=reason,
                score=score,
                current_price=current_price,
                time_horizon=TimeHorizon.LONG_TERM,
                target_price=graham_price,
                details={
                    'eps': eps,
                    'book_value': book_value,
                    'graham_price': graham_price,
                    'discount_pct': discount_pct,
                    'threshold': self.discount_threshold
                }
            )

        except Exception as e:
            logger.error(f"{ticker}: Graham strategy error: {e}")
            return None


class ZScoreStrategy:
    """
    Method 2: Panic Reversion (Z-Score)

    Logic: Calculate 20-day Mean and Standard Deviation
    Condition: Current Price < (Mean - 2.0 × StdDev)

    This strategy identifies statistically oversold conditions where
    price has deviated significantly below its recent average.
    """

    def __init__(self):
        self.period = settings.ZSCORE_PERIOD
        self.threshold = settings.ZSCORE_THRESHOLD
        self.min_data_points = settings.ZSCORE_MIN_DATA_POINTS

    def evaluate(self, ticker: str) -> Optional[StrategyResult]:
        """
        Evaluate stock using Z-Score method.

        Args:
            ticker: Stock ticker symbol

        Returns:
            StrategyResult or None if evaluation fails
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f"{self.period + 10}d", interval="1d")

            if hist.empty or len(hist) < self.min_data_points:
                logger.debug(f"{ticker}: Insufficient data for Z-Score")
                return None

            # Get closing prices
            prices = hist['Close'].values[-self.period:]
            current_price = prices[-1]

            # Calculate Z-Score
            mean_price = np.mean(prices)
            std_price = np.std(prices)

            if std_price == 0:
                logger.debug(f"{ticker}: Zero standard deviation")
                return None

            z_score = (current_price - mean_price) / std_price

            # Check if undervalued (oversold)
            is_undervalued = z_score < self.threshold

            # Calculate confidence score
            if is_undervalued:
                # More negative Z-score = higher confidence
                score = min(100, 60 + abs(z_score - self.threshold) * 20)
            else:
                score = max(0, 50 - abs(z_score) * 10)

            deviation_pct = ((current_price - mean_price) / mean_price) * 100

            reason = (
                f"Z-Score: {z_score:.2f} "
                f"({'OVERSOLD' if is_undervalued else 'NORMAL'}, "
                f"threshold: {self.threshold}, "
                f"{deviation_pct:+.1f}% from mean)"
            )

            return StrategyResult(
                is_undervalued=is_undervalued,
                method_name="Z-Score",
                reason=reason,
                score=score,
                current_price=current_price,
                time_horizon=TimeHorizon.SHORT_TERM,
                target_price=mean_price,
                details={
                    'z_score': z_score,
                    'mean_price': mean_price,
                    'std_price': std_price,
                    'deviation_pct': deviation_pct,
                    'threshold': self.threshold
                }
            )

        except Exception as e:
            logger.error(f"{ticker}: Z-Score strategy error: {e}")
            return None


class LinearRegressionStrategy:
    """
    Method 3: Trend Deviation (Linear Regression)

    Logic: Use sklearn LinearRegression on 6 months of data
    Condition: Positive slope (uptrend) AND Current Price > 10% below trend line

    This strategy identifies stocks in an uptrend that have temporarily
    dipped below their trajectory, presenting a buying opportunity.
    """

    def __init__(self):
        self.lookback_months = settings.REGRESSION_LOOKBACK_MONTHS
        self.deviation_threshold = settings.REGRESSION_DEVIATION_THRESHOLD
        self.min_slope = settings.REGRESSION_MIN_SLOPE
        self.min_r_squared = settings.REGRESSION_MIN_R_SQUARED

    def evaluate(self, ticker: str) -> Optional[StrategyResult]:
        """
        Evaluate stock using Linear Regression method.

        Args:
            ticker: Stock ticker symbol

        Returns:
            StrategyResult or None if evaluation fails
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=f"{self.lookback_months}mo", interval="1d")

            if hist.empty or len(hist) < 30:
                logger.debug(f"{ticker}: Insufficient data for regression")
                return None

            # Prepare data
            prices = hist['Close'].values
            X = np.arange(len(prices)).reshape(-1, 1)
            y = prices

            # Fit linear regression
            model = LinearRegression()
            model.fit(X, y)

            # Get predictions
            trend_line = model.predict(X)
            current_price = prices[-1]
            trend_price = trend_line[-1]
            slope = model.coef_[0]
            r_squared = model.score(X, y)

            # Calculate deviation from trend
            deviation_pct = ((current_price - trend_price) / trend_price)

            # Check conditions
            is_positive_slope = slope > self.min_slope
            is_below_trend = deviation_pct < -self.deviation_threshold
            is_good_fit = r_squared >= self.min_r_squared

            is_undervalued = is_positive_slope and is_below_trend and is_good_fit

            # Calculate confidence score
            if is_undervalued:
                # Consider slope strength and deviation magnitude
                slope_score = min(40, abs(slope) * 1000)
                deviation_score = min(40, abs(deviation_pct) * 200)
                fit_score = min(20, r_squared * 20)
                score = slope_score + deviation_score + fit_score
            else:
                score = 0

            reason = (
                f"Regression: "
                f"{'UPTREND' if is_positive_slope else 'DOWNTREND'}, "
                f"{deviation_pct*100:+.1f}% from trend "
                f"(R²={r_squared:.2f}, "
                f"{'UNDERVALUED' if is_undervalued else 'NOT TRIGGERED'})"
            )

            return StrategyResult(
                is_undervalued=is_undervalued,
                method_name="Linear Regression",
                reason=reason,
                score=score,
                current_price=current_price,
                time_horizon=TimeHorizon.SWING_TRADE,
                target_price=trend_price,
                details={
                    'slope': slope,
                    'r_squared': r_squared,
                    'trend_price': trend_price,
                    'deviation_pct': deviation_pct * 100,
                    'is_uptrend': is_positive_slope,
                    'is_good_fit': is_good_fit
                }
            )

        except Exception as e:
            logger.error(f"{ticker}: Regression strategy error: {e}")
            return None


class ValuationEngine:
    """
    Main engine that coordinates all three valuation strategies.
    """

    def __init__(self):
        self.graham = GrahamNumberStrategy()
        self.zscore = ZScoreStrategy()
        self.regression = LinearRegressionStrategy()

    def evaluate_all(self, ticker: str) -> Dict[str, Optional[StrategyResult]]:
        """
        Run all three strategies on a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary mapping strategy name to result
        """
        results = {}

        # Method 1: Graham Number
        results['graham'] = self.graham.evaluate(ticker)

        # Method 2: Z-Score
        results['zscore'] = self.zscore.evaluate(ticker)

        # Method 3: Linear Regression
        results['regression'] = self.regression.evaluate(ticker)

        return results

    def get_best_strategy(self, results: Dict[str, Optional[StrategyResult]]) -> Optional[StrategyResult]:
        """
        Get the best strategy result (highest score among undervalued signals).

        Args:
            results: Dictionary of strategy results

        Returns:
            Best StrategyResult or None
        """
        undervalued = [
            result for result in results.values()
            if result and result.is_undervalued
        ]

        if not undervalued:
            return None

        # Return highest scoring strategy
        return max(undervalued, key=lambda x: x.score)

    def get_all_undervalued(self, results: Dict[str, Optional[StrategyResult]]) -> Dict[TimeHorizon, StrategyResult]:
        """
        Get all undervalued strategy results, grouped by time horizon.

        Args:
            results: Dictionary of strategy results

        Returns:
            Dictionary mapping TimeHorizon to StrategyResult
        """
        categorized = {}

        for result in results.values():
            if result and result.is_undervalued:
                categorized[result.time_horizon] = result

        return categorized

    def format_results(self, ticker: str, results: Dict[str, Optional[StrategyResult]]) -> str:
        """Generate formatted summary of all strategy results."""
        lines = [f"\n{'='*60}", f"Valuation Analysis: {ticker}", f"{'='*60}"]

        for name, result in results.items():
            if result:
                status = "✓ UNDERVALUED" if result.is_undervalued else "✗ Not Triggered"
                lines.append(f"\n{result.method_name}: {status}")
                lines.append(f"  Score: {result.score:.1f}/100")
                lines.append(f"  {result.reason}")
            else:
                lines.append(f"\n{name.title()}: ✗ Failed to evaluate")

        lines.append(f"{'='*60}")
        return "\n".join(lines)


if __name__ == '__main__':
    # Test the strategies
    logging.basicConfig(level=logging.INFO)

    engine = ValuationEngine()
    test_ticker = 'AAPL'

    print(f"\nTesting Valuation Engine on {test_ticker}")
    results = engine.evaluate_all(test_ticker)
    print(engine.format_results(test_ticker, results))

    best = engine.get_best_strategy(results)
    if best:
        print(f"\nBest Strategy: {best.method_name} (Score: {best.score:.1f})")
    else:
        print("\nNo undervalued signals found")
