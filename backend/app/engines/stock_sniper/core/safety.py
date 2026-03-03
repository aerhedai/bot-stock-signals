"""
Safety Module - Market Regime & Earnings Trap Checks

This module implements safety mechanisms to prevent trading during
unfavourable market conditions or before major catalysts.
"""

import logging
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Tuple, Optional
from dataclasses import dataclass

# Import settings
from app.engines.stock_sniper.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SafetyCheckResult:
    """Result from safety checks."""
    is_safe: bool
    market_regime_ok: bool
    no_earnings_trap: bool
    reason: str
    spy_price: Optional[float] = None
    spy_sma: Optional[float] = None
    earnings_date: Optional[datetime] = None
    days_to_earnings: Optional[int] = None


class MarketRegimeChecker:
    """
    Checks overall market health using SPY vs 200-day SMA.

    If SPY is below its 200-day SMA, the market is in a bearish regime
    and we should avoid new positions.
    """

    def __init__(self):
        self.spy_ticker = 'SPY'
        self.sma_period = settings.SPY_SMA_PERIOD

    def check_market_regime(self) -> Tuple[bool, Optional[float], Optional[float]]:
        """
        Check if market is in favourable regime.

        Returns:
            Tuple of (is_healthy, spy_price, spy_200sma)
        """
        if not settings.MARKET_CHECK_ENABLED:
            logger.info("Market regime check disabled in settings")
            return True, None, None

        try:
            logger.info(f"Checking market regime using {self.spy_ticker}")

            # Fetch SPY data
            spy = yf.Ticker(self.spy_ticker)
            hist = spy.history(period=f"{self.sma_period + 10}d")

            if hist.empty or len(hist) < self.sma_period:
                logger.warning(f"Insufficient data for {self.spy_ticker}, skipping check")
                return True, None, None  # Default to safe if no data

            # Calculate 200-day SMA
            spy_sma_200 = hist['Close'].rolling(window=self.sma_period).mean().iloc[-1]
            spy_current_price = hist['Close'].iloc[-1]

            is_healthy = spy_current_price >= spy_sma_200

            logger.info(
                f"Market Regime: SPY=${spy_current_price:.2f}, "
                f"200-SMA=${spy_sma_200:.2f}, "
                f"Status={'✓ HEALTHY' if is_healthy else '✗ BEARISH'}"
            )

            return is_healthy, float(spy_current_price), float(spy_sma_200)

        except Exception as e:
            logger.error(f"Error checking market regime: {e}", exc_info=True)
            # On error, default to safe (don't block scanning)
            return True, None, None


class EarningsTrapChecker:
    """
    Checks if a stock has earnings announcement within buffer period.

    Earnings announcements cause high volatility and can invalidate
    technical analysis, so we avoid positions before earnings.
    """

    def __init__(self):
        self.buffer_days = settings.EARNINGS_BUFFER_DAYS

    def check_earnings_trap(self, ticker: str) -> Tuple[bool, Optional[datetime], Optional[int]]:
        """
        Check if stock has earnings within buffer period.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Tuple of (is_safe, earnings_date, days_until_earnings)
        """
        if not settings.EARNINGS_CHECK_ENABLED:
            return True, None, None

        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Try to get earnings date
            earnings_date = None

            # Check multiple possible fields
            if 'earningsDate' in info and info['earningsDate']:
                # earningsDate can be a timestamp or list of timestamps
                earnings_data = info['earningsDate']
                if isinstance(earnings_data, list) and len(earnings_data) > 0:
                    earnings_date = earnings_data[0]
                else:
                    earnings_date = earnings_data

            # Convert to datetime if we got a value
            if earnings_date:
                if isinstance(earnings_date, (int, float)):
                    earnings_date = datetime.fromtimestamp(earnings_date)
                elif not isinstance(earnings_date, datetime):
                    # Try parsing as date
                    try:
                        earnings_date = pd.to_datetime(earnings_date)
                    except:
                        earnings_date = None

            if not earnings_date:
                # No earnings date found, assume safe
                logger.debug(f"{ticker}: No earnings date found, assuming safe")
                return True, None, None

            # Calculate days until earnings
            days_until = (earnings_date - datetime.now()).days

            # Check if within buffer period
            is_safe = days_until > self.buffer_days or days_until < 0

            if not is_safe:
                logger.info(
                    f"{ticker}: EARNINGS TRAP - "
                    f"Earnings in {days_until} days "
                    f"(buffer: {self.buffer_days} days)"
                )

            return is_safe, earnings_date, days_until

        except Exception as e:
            logger.debug(f"{ticker}: Error checking earnings: {e}")
            # On error, default to safe (don't block unnecessarily)
            return True, None, None


class SafetyManager:
    """
    Main safety manager that coordinates all safety checks.
    """

    def __init__(self):
        self.market_checker = MarketRegimeChecker()
        self.earnings_checker = EarningsTrapChecker()
        self._market_cache = None
        self._market_cache_time = None
        self._cache_duration = timedelta(minutes=30)

    def check_market_safety(self) -> Tuple[bool, Optional[float], Optional[float]]:
        """
        Check market regime with caching.

        Returns:
            Tuple of (is_safe, spy_price, spy_sma)
        """
        now = datetime.now()

        # Use cache if available and fresh
        if self._market_cache and self._market_cache_time:
            if now - self._market_cache_time < self._cache_duration:
                logger.debug("Using cached market regime check")
                return self._market_cache

        # Perform fresh check
        result = self.market_checker.check_market_regime()
        self._market_cache = result
        self._market_cache_time = now

        return result

    def check_stock_safety(self, ticker: str) -> SafetyCheckResult:
        """
        Perform comprehensive safety check for a stock.

        Args:
            ticker: Stock ticker symbol

        Returns:
            SafetyCheckResult object with all safety information
        """
        # Check market regime
        market_ok, spy_price, spy_sma = self.check_market_safety()

        # Check earnings trap
        earnings_ok, earnings_date, days_to_earnings = \
            self.earnings_checker.check_earnings_trap(ticker)

        # Determine overall safety
        is_safe = market_ok and earnings_ok

        # Build reason message
        reasons = []
        if not market_ok:
            reasons.append("Market bearish (SPY < 200-SMA)")
        if not earnings_ok:
            reasons.append(f"Earnings in {days_to_earnings} days")

        reason = "; ".join(reasons) if reasons else "All checks passed"

        return SafetyCheckResult(
            is_safe=is_safe,
            market_regime_ok=market_ok,
            no_earnings_trap=earnings_ok,
            reason=reason,
            spy_price=spy_price,
            spy_sma=spy_sma,
            earnings_date=earnings_date,
            days_to_earnings=days_to_earnings
        )

    def get_safety_report(self, result: SafetyCheckResult) -> str:
        """Generate human-readable safety report."""
        report = []
        report.append(f"Safety Status: {'✓ SAFE' if result.is_safe else '✗ UNSAFE'}")

        if result.spy_price and result.spy_sma:
            market_status = "✓" if result.market_regime_ok else "✗"
            report.append(
                f"{market_status} Market: SPY ${result.spy_price:.2f} "
                f"vs 200-SMA ${result.spy_sma:.2f}"
            )

        if result.days_to_earnings is not None:
            earnings_status = "✓" if result.no_earnings_trap else "✗"
            report.append(
                f"{earnings_status} Earnings: {result.days_to_earnings} days away"
            )

        if not result.is_safe:
            report.append(f"Reason: {result.reason}")

        return "\n".join(report)


# Singleton instance
_safety_manager = None

def get_safety_manager() -> SafetyManager:
    """Get or create the global SafetyManager instance."""
    global _safety_manager
    if _safety_manager is None:
        _safety_manager = SafetyManager()
    return _safety_manager


# Convenience functions
def check_market_safety() -> Tuple[bool, Optional[float], Optional[float]]:
    """Quick check of market safety."""
    return get_safety_manager().check_market_safety()


def check_stock_safety(ticker: str) -> SafetyCheckResult:
    """Quick check of individual stock safety."""
    return get_safety_manager().check_stock_safety(ticker)


if __name__ == '__main__':
    # Test the safety checks
    logging.basicConfig(level=logging.INFO)

    print("Testing Safety Module")
    print("=" * 60)

    # Test market regime
    is_safe, spy_price, spy_sma = check_market_safety()
    print(f"\n Market Regime:")
    print(f"  SPY Price: ${spy_price:.2f}" if spy_price else "  SPY Price: N/A")
    print(f"  200-SMA: ${spy_sma:.2f}" if spy_sma else "  200-SMA: N/A")
    print(f"  Status: {'SAFE ✓' if is_safe else 'UNSAFE ✗'}")

    # Test stock safety
    test_ticker = 'AAPL'
    print(f"\n Stock Safety Check ({test_ticker}):")
    result = check_stock_safety(test_ticker)
    print(get_safety_manager().get_safety_report(result))
