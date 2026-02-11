"""Crypto signal API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends

from app.dependencies import get_scheduler, get_alert_store
from app.models.common import ScanResultResponse
from app.models.crypto import CryptoAlertHistoryResponse, CryptoWatchlistResponse
from app.services.scheduler import SchedulerService

router = APIRouter(prefix="/crypto", tags=["crypto"])


@router.get("/signals", response_model=CryptoAlertHistoryResponse)
async def get_crypto_signals(store=Depends(get_alert_store)):
    """Get crypto alert history from JSON."""
    data = store.get_crypto_alerts()
    # Crypto alerts format: {symbol: timestamp_str}
    return CryptoAlertHistoryResponse(
        total_alerts=len(data), alerts=data
    )


@router.get("/watchlist", response_model=CryptoWatchlistResponse)
async def get_crypto_watchlist():
    """Get crypto watchlist organized by category."""
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
