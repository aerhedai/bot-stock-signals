"""
Stock Scanner - Main Scanning Logic

Integrates safety checks, valuation strategies, and technical triggers
to identify high-probability undervalued stock opportunities.
"""

import logging
import time
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from datetime import datetime

from app.engines.stock_sniper.config import settings
from app.engines.stock_sniper.core.safety import SafetyManager, SafetyCheckResult
from app.engines.stock_sniper.core.strategies import ValuationEngine, StrategyResult, TimeHorizon

logger = logging.getLogger(__name__)


@dataclass
class TriggerResult:
    """Result from technical trigger check."""
    is_triggered: bool
    current_price: float
    ema_value: float
    price_above_ema: bool
    reason: str


@dataclass
class SniperSignal:
    """Complete signal from the sniper scanner."""
    ticker: str
    timestamp: datetime

    # Safety
    safety_result: SafetyCheckResult

    # Strategy (best scoring)
    strategy_result: StrategyResult

    # All categorized strategies
    categorized_strategies: Dict[TimeHorizon, StrategyResult]

    # Trigger
    trigger_result: TriggerResult

    # Overall
    is_valid_signal: bool
    should_alert: bool


class EMATrigger:
    """
    Technical trigger using Exponential Moving Average.

    Only alerts when price closes above the 20-EMA, indicating
    momentum is shifting in our favour after finding undervaluation.
    """

    def __init__(self):
        self.ema_period = settings.EMA_PERIOD
        self.timeframe = settings.EMA_TIMEFRAME
        self.min_data_points = settings.EMA_MIN_DATA_POINTS

    def calculate_ema(self, prices: np.ndarray, period: int) -> np.ndarray:
        """
        Calculate Exponential Moving Average.

        Args:
            prices: Array of prices
            period: EMA period

        Returns:
            Array of EMA values
        """
        return pd.Series(prices).ewm(span=period, adjust=False).mean().values

    def check_trigger(self, ticker: str) -> Optional[TriggerResult]:
        """
        Check if EMA trigger is activated.

        Args:
            ticker: Stock ticker symbol

        Returns:
            TriggerResult or None if check fails
        """
        try:
            stock = yf.Ticker(ticker)

            # Fetch data based on timeframe
            if self.timeframe == '4h':
                hist = stock.history(period="60d", interval="1h")
                # Resample to 4h
                hist = hist.resample('4H').agg({
                    'Open': 'first',
                    'High': 'max',
                    'Low': 'min',
                    'Close': 'last',
                    'Volume': 'sum'
                }).dropna()
            else:  # daily
                hist = stock.history(period=f"{self.min_data_points + 10}d", interval="1d")

            if hist.empty or len(hist) < self.min_data_points:
                logger.debug(f"{ticker}: Insufficient data for EMA trigger")
                return None

            # Use only closed candles (index -1, not current/incomplete candle)
            if settings.USE_CLOSED_CANDLES_ONLY:
                prices = hist['Close'].values[:-1] if len(hist) > 1 else hist['Close'].values
                current_price = prices[-1]
            else:
                prices = hist['Close'].values
                current_price = prices[-1]

            # Calculate EMA
            ema_values = self.calculate_ema(prices, self.ema_period)
            ema_current = ema_values[-1]

            # Check if price is above EMA
            price_above_ema = current_price > ema_current

            # Determine if triggered
            is_triggered = price_above_ema if settings.REQUIRE_PRICE_ABOVE_EMA else True

            distance_pct = ((current_price - ema_current) / ema_current) * 100

            reason = (
                f"Price ${current_price:.2f} "
                f"{'ABOVE' if price_above_ema else 'BELOW'} "
                f"EMA(20) ${ema_current:.2f} "
                f"({distance_pct:+.2f}%)"
            )

            return TriggerResult(
                is_triggered=is_triggered,
                current_price=current_price,
                ema_value=ema_current,
                price_above_ema=price_above_ema,
                reason=reason
            )

        except Exception as e:
            logger.error(f"{ticker}: EMA trigger error: {e}")
            return None


class SniperScanner:
    """
    Main scanner that orchestrates the complete sniper signal detection.

    Pipeline:
    1. Safety Check (Market + Earnings)
    2. Strategy Evaluation (3 methods)
    3. Technical Trigger (EMA)
    4. Generate Signal
    """

    def __init__(self):
        self.safety_manager = SafetyManager()
        self.valuation_engine = ValuationEngine()
        self.ema_trigger = EMATrigger()

    def scan_single(self, ticker: str, verbose: bool = False) -> Optional[SniperSignal]:
        """
        Scan a single ticker through the complete pipeline.

        Args:
            ticker: Stock ticker symbol
            verbose: Enable detailed logging

        Returns:
            SniperSignal or None if scan fails
        """
        if verbose:
            logger.info(f"\n{'='*60}\nScanning: {ticker}\n{'='*60}")

        try:
            # Step 1: Safety Check
            if verbose:
                logger.info(f"{ticker}: Step 1/3 - Safety checks...")

            safety_result = self.safety_manager.check_stock_safety(ticker)

            if not safety_result.is_safe:
                if verbose:
                    logger.info(f"{ticker}: ✗ BLOCKED by safety: {safety_result.reason}")
                return None

            if verbose:
                logger.info(f"{ticker}: ✓ Safety checks passed")

            # Step 2: Strategy Evaluation
            if verbose:
                logger.info(f"{ticker}: Step 2/3 - Valuation strategies...")

            strategy_results = self.valuation_engine.evaluate_all(ticker)
            best_strategy = self.valuation_engine.get_best_strategy(strategy_results)
            categorized_strategies = self.valuation_engine.get_all_undervalued(strategy_results)

            if not best_strategy:
                if verbose:
                    logger.info(f"{ticker}: ✗ No undervaluation detected")
                return None

            if verbose:
                logger.info(
                    f"{ticker}: ✓ Undervalued by {best_strategy.method_name} "
                    f"(Score: {best_strategy.score:.1f})"
                )
                if len(categorized_strategies) > 1:
                    logger.info(
                        f"{ticker}: ℹ️  Multiple time horizons available: "
                        f"{', '.join([h.value for h in categorized_strategies.keys()])}"
                    )

            # Step 3: Technical Trigger
            if verbose:
                logger.info(f"{ticker}: Step 3/3 - Technical trigger...")

            trigger_result = self.ema_trigger.check_trigger(ticker)

            if not trigger_result:
                if verbose:
                    logger.info(f"{ticker}: ✗ Trigger check failed (data issue)")
                return None

            if not trigger_result.is_triggered:
                if verbose:
                    logger.info(f"{ticker}: ⏳ Waiting for trigger: {trigger_result.reason}")

            # Create signal
            is_valid_signal = trigger_result.is_triggered
            should_alert = is_valid_signal

            if verbose and is_valid_signal:
                logger.info(f"{ticker}: ✓✓✓ VALID SIGNAL DETECTED!")

            return SniperSignal(
                ticker=ticker,
                timestamp=datetime.now(),
                safety_result=safety_result,
                strategy_result=best_strategy,
                categorized_strategies=categorized_strategies,
                trigger_result=trigger_result,
                is_valid_signal=is_valid_signal,
                should_alert=should_alert
            )

        except Exception as e:
            logger.error(f"{ticker}: Scanner error: {e}", exc_info=True)
            return None

    def scan_multiple(
        self,
        tickers: List[str],
        verbose: bool = False,
        stop_on_signal: bool = False
    ) -> List[SniperSignal]:
        """
        Scan multiple tickers.

        Args:
            tickers: List of ticker symbols
            verbose: Enable detailed logging
            stop_on_signal: Stop after finding first valid signal

        Returns:
            List of valid SniperSignals
        """
        logger.info(f"Starting scan of {len(tickers)} tickers...")

        valid_signals = []
        scanned = 0
        errors = 0

        for ticker in tickers:
            try:
                if scanned > 0:
                    time.sleep(settings.REQUEST_DELAY_SECONDS)

                signal = self.scan_single(ticker, verbose=verbose)

                if signal and signal.is_valid_signal:
                    valid_signals.append(signal)
                    logger.info(
                        f"✓ SIGNAL: {ticker} via {signal.strategy_result.method_name} "
                        f"(Score: {signal.strategy_result.score:.1f})"
                    )

                    if stop_on_signal:
                        logger.info("Stopping scan after finding valid signal")
                        break

                scanned += 1

            except Exception as e:
                logger.error(f"{ticker}: Error during scan: {e}")
                errors += 1
                continue

        logger.info(
            f"Scan complete: {scanned} scanned, "
            f"{len(valid_signals)} signals, {errors} errors"
        )

        return valid_signals

    def format_signal(self, signal: SniperSignal) -> str:
        """Generate formatted signal report."""
        lines = [
            f"\n{'='*60}",
            f"🎯 SNIPER SIGNAL: {signal.ticker}",
            f"{'='*60}",
            f"Timestamp: {signal.timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]

        # Show all categorized strategies
        if len(signal.categorized_strategies) > 0:
            lines.append("⏱️  TIME HORIZONS AVAILABLE:")

            horizon_order = [TimeHorizon.SHORT_TERM, TimeHorizon.SWING_TRADE, TimeHorizon.LONG_TERM]
            for horizon in horizon_order:
                if horizon in signal.categorized_strategies:
                    strat = signal.categorized_strategies[horizon]
                    emoji = "⚡" if horizon == TimeHorizon.SHORT_TERM else "🌊" if horizon == TimeHorizon.SWING_TRADE else "🏔️"

                    lines.append(f"\n  {emoji} {horizon.value}")
                    lines.append(f"     Method: {strat.method_name}")
                    lines.append(f"     Score: {strat.score:.1f}/100")
                    lines.append(f"     Current: ${strat.current_price:.2f}")
                    if strat.target_price:
                        upside = ((strat.target_price - strat.current_price) / strat.current_price) * 100
                        lines.append(f"     Target: ${strat.target_price:.2f} (+{upside:.1f}%)")

            lines.append("")

        # Primary signal
        lines.append(f"⭐ PRIMARY SIGNAL: {signal.strategy_result.method_name}")
        lines.append(f"  {signal.strategy_result.reason}")
        lines.append("")

        lines.append(f"📊 TRIGGER:")
        lines.append(f"  {signal.trigger_result.reason}")
        lines.append(f"  Status: {'✓ TRIGGERED' if signal.trigger_result.is_triggered else '⏳ WAITING'}")
        lines.append("")

        lines.append(f"🛡️  SAFETY:")
        lines.append(f"  Market: {'✓ OK' if signal.safety_result.market_regime_ok else '✗ BEARISH'}")
        lines.append(f"  Earnings: {'✓ Safe' if signal.safety_result.no_earnings_trap else '✗ Trap'}")
        lines.append("")
        lines.append(f"{'='*60}")

        return "\n".join(lines)


# Singleton instance
_scanner = None

def get_scanner() -> SniperScanner:
    """Get or create the global SniperScanner instance."""
    global _scanner
    if _scanner is None:
        _scanner = SniperScanner()
    return _scanner


if __name__ == '__main__':
    # Test the scanner
    logging.basicConfig(level=logging.INFO)

    scanner = get_scanner()
    test_ticker = 'AAPL'

    print(f"\nTesting Sniper Scanner on {test_ticker}")
    signal = scanner.scan_single(test_ticker, verbose=True)

    if signal:
        print(scanner.format_signal(signal))
    else:
        print(f"\nNo signal generated for {test_ticker}")
