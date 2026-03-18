"""Crypto signal API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends

from app.dependencies import get_scheduler, get_alert_store
from app.models.common import ScanResultResponse
from app.models.crypto import CryptoAlertHistoryResponse, CryptoSignalResponse, CryptoWatchlistResponse
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
