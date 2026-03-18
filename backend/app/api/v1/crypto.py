"""Crypto signal API endpoints."""

import asyncio
from datetime import datetime
from math import isnan

import pandas as pd
import yfinance as yf
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_scheduler, get_alert_store
from app.models.common import ScanResultResponse
from app.models.crypto import (
    CryptoAlertHistoryResponse, CryptoSignalResponse, CryptoWatchlistResponse,
    CryptoChartResponse, CryptoChartPoint,
)
from app.services.scheduler import SchedulerService

router = APIRouter(prefix="/crypto", tags=["crypto"])


@router.get("/signals", response_model=CryptoAlertHistoryResponse)
async def get_crypto_signals(store=Depends(get_alert_store)):
    """Get the latest crypto prediction per symbol."""
    data = store.get_crypto_alerts()
    raw_alerts = data.get("alerts", {})

    alerts: dict[str, CryptoSignalResponse] = {}
    for symbol, entry in raw_alerts.items():
        # Skip legacy entries that only stored a timestamp string
        if isinstance(entry, str):
            continue

        alerts[symbol] = CryptoSignalResponse(
            symbol=entry.get("symbol", symbol),
            name=entry.get("name", symbol),
            category=entry.get("category", ""),
            current_price=entry.get("current_price", 0),
            valuation_method=entry.get("valuation_method", ""),
            valuation_score=entry.get("valuation_score", 0),
            fair_value_estimate=entry.get("fair_value_estimate"),
            discount_percentage=entry.get("discount_percentage"),
            trigger_type=entry.get("trigger_type", ""),
            trigger_description=entry.get("trigger_description", ""),
            rsi=entry.get("rsi"),
            bollinger_position=entry.get("bollinger_position"),
            change_24h=entry.get("change_24h"),
            change_7d=entry.get("change_7d"),
            severity=entry.get("severity", "medium"),
            confidence=entry.get("confidence", "medium"),
            combined_score=entry.get("combined_score", 0),
            timestamp=entry.get("timestamp", ""),
        )

    return CryptoAlertHistoryResponse(
        total_alerts=len(alerts),
        alerts=alerts,
    )


@router.get("/chart/{symbol:path}", response_model=CryptoChartResponse)
async def get_crypto_chart(symbol: str, store=Depends(get_alert_store)):
    """Return 60 days of daily price + Bollinger Bands + RSI data for a crypto symbol."""
    def _fetch():
        hist = yf.Ticker(symbol).history(period="60d", interval="1d")
        if hist.empty:
            return None
        closes = pd.Series(hist["Close"].values, dtype=float)

        # Bollinger Bands (20-period, 2 std dev)
        bb_mid = closes.rolling(20).mean()
        bb_std = closes.rolling(20).std()
        bb_upper = bb_mid + 2 * bb_std
        bb_lower = bb_mid - 2 * bb_std

        # RSI-14
        delta = closes.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        def _safe(val):
            try:
                f = float(val)
                return None if isnan(f) else round(f, 6)
            except (TypeError, ValueError):
                return None

        points = []
        for i, (date, price) in enumerate(zip(hist.index, closes)):
            points.append(CryptoChartPoint(
                date=date.strftime("%Y-%m-%d"),
                price=round(float(price), 6),
                bb_upper=_safe(bb_upper.iloc[i]),
                bb_mid=_safe(bb_mid.iloc[i]),
                bb_lower=_safe(bb_lower.iloc[i]),
                rsi=_safe(rsi.iloc[i]),
            ))
        return points

    points = await asyncio.to_thread(_fetch)
    if points is None:
        raise HTTPException(status_code=404, detail=f"No data found for {symbol}")

    # Pull signal metadata from the alert store
    raw_alerts = store.get_crypto_alerts().get("alerts", {})
    entry = raw_alerts.get(symbol)
    if isinstance(entry, str):
        entry = None

    fair_value = entry.get("fair_value_estimate") if entry else None
    signal_date = entry.get("timestamp", "")[:10] if entry else None
    signal_price = entry.get("current_price") if entry else None

    return CryptoChartResponse(
        symbol=symbol,
        data=points,
        fair_value=fair_value,
        signal_date=signal_date,
        signal_price=signal_price,
    )


@router.get("/watchlist", response_model=CryptoWatchlistResponse)
async def get_crypto_watchlist():
    """Get crypto watchlist organised by category."""
    from app.engines.crypto_sniper.config.crypto_list import (
        CRYPTO_WATCHLIST, MAJOR_CRYPTOS, DEFI_CRYPTOS, ALT_CRYPTOS, STABLECOINS,
    )

    categories = {
        "Major": MAJOR_CRYPTOS,
        "DeFi": DEFI_CRYPTOS,
        "Alt": ALT_CRYPTOS,
        "Stablecoins": STABLECOINS,
    }

    return CryptoWatchlistResponse(
        total=len(CRYPTO_WATCHLIST), categories=categories
    )


@router.post("/scan", response_model=ScanResultResponse)
async def trigger_crypto_scan(scheduler: SchedulerService = Depends(get_scheduler)):
    """Trigger an immediate crypto scan."""
    await scheduler._run_crypto_scan()
    return ScanResultResponse(
        service="crypto_sniper",
        triggered=True,
        message=f"Scan complete. {scheduler.stats.crypto_last_signals} signals found.",
        timestamp=datetime.now(),
    )
