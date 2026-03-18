"""
Cryptocurrency Price Monitor

Two-layer approach:
1. Find undervalued cryptocurrencies (valuation layer)
2. Detect valid technical triggers (timing layer)
3. Alert only when BOTH conditions are met
"""

import logging
import time
import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import pandas as pd

from app.engines.crypto_sniper.config import settings
from app.engines.crypto_sniper.config.crypto_list import get_crypto_name, get_crypto_category
from app.engines.crypto_sniper.core.indicators import TechnicalIndicators
from app.engines.crypto_sniper.core.valuation import CryptoValuation, ValuationResult

logger = logging.getLogger(__name__)


@dataclass
class CryptoSignal:
    """Represents a cryptocurrency alert signal with both valuation and technical data."""
    # Required fields (no defaults)
    symbol: str
    name: str
    category: str
    current_price: float
    valuation_method: str  # Which valuation method triggered
    valuation_score: float  # 0-100 score from valuation
    trigger_type: str  # What technical indicator triggered entry

    # Optional fields (with defaults)
    fair_value_estimate: Optional[float] = None
    discount_percentage: Optional[float] = None
    trigger_description: str = ""

    # Price changes
    change_1h: Optional[float] = None
    change_24h: Optional[float] = None
    change_7d: Optional[float] = None

    # Technical indicators
    rsi: Optional[float] = None
    macd: Optional[Dict[str, float]] = None
    bollinger_position: Optional[str] = None
    volume_change: Optional[float] = None

    # Signal metadata
    severity: str = "medium"  # 'low', 'medium', 'high', 'critical'
    confidence: str = "medium"  # Confidence in the signal
    combined_score: float = 0.0  # Combined valuation + technical score
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class CryptoMonitor:
    """
    Monitors cryptocurrency prices using two-layer approach:
    Layer 1: Valuation - Is it undervalued?
    Layer 2: Technical - Is it time to enter?
    """

    def __init__(self):
        """Initialise the crypto monitor."""
        self.indicators = TechnicalIndicators()
        self.valuation = CryptoValuation()
        self.btc_data_cache = None  # Cache BTC data for relative strength
        self.btc_cache_time = None
        logger.info("CryptoMonitor initialised with two-layer approach")

    def fetch_crypto_data(
        self,
        symbol: str,
        period: str = '6mo',
        interval: str = '1d'
    ) -> Optional[pd.DataFrame]:
        """
        Fetch cryptocurrency price data from Yahoo Finance.

        Args:
            symbol: Crypto symbol (e.g., 'BTC-USD')
            period: Data period ('1d', '7d', '1mo', '6mo', '1y', etc.)
            interval: Data interval ('1m', '5m', '1h', '1d', etc.)

        Returns:
            DataFrame with OHLCV data or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)

            if data.empty:
                logger.warning(f"No data returned for {symbol}")
                return None

            return data

        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {e}")
            return None

    def get_btc_data(self) -> Optional[pd.DataFrame]:
        """
        Get Bitcoin data (cached for 1 hour).

        Returns:
            BTC price data or None
        """
        now = datetime.now()

        # Return cached data if less than 1 hour old
        if self.btc_data_cache is not None and self.btc_cache_time is not None:
            if (now - self.btc_cache_time).total_seconds() < 3600:
                return self.btc_data_cache

        # Fetch fresh BTC data
        btc_data = self.fetch_crypto_data('BTC-USD', period='6mo', interval='1d')
        if btc_data is not None:
            self.btc_data_cache = btc_data
            self.btc_cache_time = now

        return btc_data

    def calculate_price_changes(self, data: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate price changes over different timeframes.

        Args:
            data: DataFrame with price data (daily interval)

        Returns:
            Dict with price changes for 1d, 7d, 30d
        """
        changes = {}

        try:
            current_price = float(data['Close'].iloc[-1])

            # 1 day change
            if len(data) > 1:
                price_1d_ago = float(data['Close'].iloc[-2])
                changes['1d'] = ((current_price - price_1d_ago) / price_1d_ago) * 100

            # 7 day change
            if len(data) >= 7:
                price_7d_ago = float(data['Close'].iloc[-7])
                changes['7d'] = ((current_price - price_7d_ago) / price_7d_ago) * 100

            # 30 day change
            if len(data) >= 30:
                price_30d_ago = float(data['Close'].iloc[-30])
                changes['30d'] = ((current_price - price_30d_ago) / price_30d_ago) * 100

        except Exception as e:
            logger.error(f"Error calculating price changes: {e}")

        return changes

    def calculate_volume_change(self, data: pd.DataFrame) -> Optional[float]:
        """
        Calculate volume change compared to average.

        Args:
            data: DataFrame with volume data

        Returns:
            Percentage volume change or None
        """
        try:
            if len(data) < 20:
                return None

            current_volume = float(data['Volume'].iloc[-1])
            avg_volume = self.indicators.calculate_volume_sma(data['Volume'], period=20)

            if avg_volume and avg_volume > 0:
                volume_change = ((current_volume - avg_volume) / avg_volume) * 100
                return volume_change

        except Exception as e:
            logger.error(f"Error calculating volume change: {e}")

        return None

    def check_technical_triggers(
        self,
        data: pd.DataFrame,
        rsi: Optional[float],
        macd: Optional[Dict[str, float]],
        bollinger_bands: Optional[Dict[str, float]]
    ) -> Optional[Dict[str, Any]]:
        """
        Check for valid technical entry triggers.

        Only triggers for BUY signals (we're looking for undervalued entries).

        Args:
            data: Price data
            rsi: RSI value
            macd: MACD data
            bollinger_bands: Bollinger Bands data

        Returns:
            Trigger info dict or None
        """
        triggers = []
        current_price = float(data['Close'].iloc[-1])

        # Trigger 1: RSI Oversold (potential bounce)
        if rsi and rsi <= settings.RSI_OVERSOLD:
            triggers.append({
                'type': 'rsi_oversold',
                'description': f"RSI oversold at {rsi:.1f}",
                'strength': 'high' if rsi <= 25 else 'medium'
            })

        # Trigger 2: Price below lower Bollinger Band (mean reversion)
        if bollinger_bands and current_price < bollinger_bands['lower']:
            deviation = ((bollinger_bands['lower'] - current_price) / bollinger_bands['lower']) * 100
            triggers.append({
                'type': 'bb_oversold',
                'description': f"Price {deviation:.1f}% below lower BB",
                'strength': 'high' if deviation > 5 else 'medium'
            })

        # Trigger 3: MACD Bullish Crossover
        if macd and macd['histogram'] > 0 and len(data) > 1:
            # Check if histogram was negative before (recent crossover)
            prev_macd = self.indicators.calculate_macd(data['Close'].iloc[:-1])
            if prev_macd and prev_macd['histogram'] <= 0:
                triggers.append({
                    'type': 'macd_crossover',
                    'description': "MACD bullish crossover",
                    'strength': 'high'
                })

        # Trigger 4: Price consolidating near support (low volatility)
        if len(data) >= 20:
            recent_prices = data['Close'].tail(10)
            volatility = (recent_prices.std() / recent_prices.mean()) * 100

            if volatility < 3.0:  # Low volatility indicates consolidation
                triggers.append({
                    'type': 'consolidation',
                    'description': f"Low volatility consolidation ({volatility:.1f}%)",
                    'strength': 'low'
                })

        # Trigger 5: Golden Cross (50/200 MA)
        if self.indicators.detect_golden_cross(data['Close'], short_period=50, long_period=200):
            triggers.append({
                'type': 'golden_cross',
                'description': "Golden cross detected (50/200 MA)",
                'strength': 'critical'
            })

        # Return strongest trigger
        if triggers:
            # Sort by strength: critical > high > medium > low
            strength_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
            triggers_sorted = sorted(triggers, key=lambda t: strength_order.get(t['strength'], 0), reverse=True)
            return triggers_sorted[0]

        return None

    def analyze_crypto(self, symbol: str) -> Optional[CryptoSignal]:
        """
        Analyse a cryptocurrency using two-layer approach.

        Layer 1: Check if undervalued
        Layer 2: Check for technical trigger

        Only returns signal if BOTH layers confirm.

        Args:
            symbol: Crypto symbol to analyse

        Returns:
            CryptoSignal if both layers confirm, None otherwise
        """
        try:
            # Fetch daily data for valuation analysis (6 months)
            data = self.fetch_crypto_data(symbol, period='6mo', interval='1d')
            if data is None or len(data) < 100:
                logger.debug(f"Insufficient data for {symbol}")
                return None

            current_price = float(data['Close'].iloc[-1])

            # ===================================================================
            # LAYER 1: VALUATION - Is it undervalued?
            # ===================================================================

            # Get BTC data for relative strength
            btc_data = self.get_btc_data()

            # Run all valuation methods
            valuation_results = self.valuation.analyze_all_methods(
                symbol=symbol,
                price_data=data,
                btc_data=btc_data
            )

            # If not undervalued by any method, skip
            if not valuation_results:
                logger.debug(f"{symbol}: Not undervalued by any method")
                return None

            # Get best valuation
            best_valuation = self.valuation.get_best_valuation(valuation_results)

            logger.info(f"{symbol}: Undervalued by {best_valuation.method_name} "
                       f"(score: {best_valuation.score:.1f}, discount: {best_valuation.discount_percentage:.1f}%)")

            # ===================================================================
            # LAYER 2: TECHNICAL TRIGGERS - Is it time to enter?
            # ===================================================================

            # Calculate technical indicators
            rsi = self.indicators.calculate_rsi(data['Close'], period=settings.RSI_PERIOD)
            macd = self.indicators.calculate_macd(data['Close'])
            bb = self.indicators.calculate_bollinger_bands(data['Close'], period=settings.BB_PERIOD)

            # Check for entry triggers
            trigger = self.check_technical_triggers(data, rsi, macd, bb)

            # If no trigger, skip (we have value but not the right entry timing)
            if not trigger:
                logger.debug(f"{symbol}: Undervalued but no technical trigger yet")
                return None

            logger.info(f"{symbol}: Technical trigger detected - {trigger['description']}")

            # ===================================================================
            # BOTH LAYERS CONFIRMED - CREATE SIGNAL
            # ===================================================================

            # Calculate price changes
            changes = self.calculate_price_changes(data)
            volume_change = self.calculate_volume_change(data)

            # Determine bollinger position
            bb_position = None
            if bb and current_price:
                if current_price > bb['upper']:
                    bb_position = 'above_upper'
                elif current_price < bb['lower']:
                    bb_position = 'below_lower'
                else:
                    bb_position = 'within_bands'

            # Calculate combined score (valuation 60% + trigger 40%)
            trigger_score_map = {'critical': 100, 'high': 80, 'medium': 60, 'low': 40}
            trigger_score = trigger_score_map.get(trigger['strength'], 50)
            combined_score = (best_valuation.score * 0.6) + (trigger_score * 0.4)

            # Determine severity based on combined score
            if combined_score >= 85:
                severity = 'critical'
            elif combined_score >= 70:
                severity = 'high'
            elif combined_score >= 50:
                severity = 'medium'
            else:
                severity = 'low'

            # Create signal
            signal = CryptoSignal(
                symbol=symbol,
                name=get_crypto_name(symbol),
                category=get_crypto_category(symbol),
                current_price=current_price,

                # Valuation layer
                valuation_method=best_valuation.method_name,
                valuation_score=best_valuation.score,
                fair_value_estimate=best_valuation.fair_value_estimate,
                discount_percentage=best_valuation.discount_percentage,

                # Technical layer
                trigger_type=trigger['type'],
                trigger_description=trigger['description'],

                # Price changes (daily data — 1d candle = closest approximation to 24 h)
                change_1h=None,
                change_24h=changes.get('1d'),
                change_7d=changes.get('7d'),

                # Technical indicators
                rsi=rsi,
                macd=macd,
                bollinger_position=bb_position,
                volume_change=volume_change,

                # Metadata
                severity=severity,
                confidence=best_valuation.confidence,
                combined_score=combined_score
            )

            logger.info(f"✓ Signal created for {symbol}: {severity.upper()} "
                       f"(combined score: {combined_score:.1f})")

            return signal

        except Exception as e:
            logger.error(f"Error analysing {symbol}: {e}", exc_info=True)
            return None

    def scan_multiple(self, symbols: List[str]) -> List[CryptoSignal]:
        """
        Scan multiple cryptocurrencies using two-layer approach.

        Args:
            symbols: List of crypto symbols

        Returns:
            List of detected signals (only when both layers confirm)
        """
        signals = []

        logger.info(f"Starting two-layer scan of {len(symbols)} cryptocurrencies")
        logger.info("Layer 1: Checking valuation (undervalued?)")
        logger.info("Layer 2: Checking technicals (entry trigger?)")

        for i, symbol in enumerate(symbols, 1):
            try:
                if i > 1:
                    time.sleep(settings.REQUEST_DELAY_SECONDS)

                logger.debug(f"[{i}/{len(symbols)}] Analysing {symbol}...")

                signal = self.analyze_crypto(symbol)
                if signal:
                    signals.append(signal)
                    logger.info(f"✓ Signal #{len(signals)}: {symbol} "
                               f"({signal.valuation_method} + {signal.trigger_type})")

            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")

        logger.info(f"Scan complete: {len(signals)} signals from {len(symbols)} cryptos")

        # Sort by combined score (best first)
        signals.sort(key=lambda s: s.combined_score, reverse=True)

        return signals
