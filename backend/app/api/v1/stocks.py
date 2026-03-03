"""Stock signal API endpoints."""

import asyncio
from datetime import datetime

from fastapi import APIRouter, Depends

from app.dependencies import get_scheduler, get_alert_store
from app.models.common import ScanResultResponse
from app.models.stocks import StockAlertHistoryResponse, StockSignalResponse, WatchlistResponse
from app.services.scheduler import SchedulerService

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/signals", response_model=StockAlertHistoryResponse)
async def get_stock_signals(store=Depends(get_alert_store)):
    """Get stock alert history from JSON."""
    data = store.get_stock_alerts()
    raw_alerts = data.get("alerts", {})

    alerts = {}
    total = 0
    for ticker, entries in raw_alerts.items():
        alerts[ticker] = [
            StockSignalResponse(
                ticker=ticker,
                method=e.get("method", ""),
                score=e.get("score", 0),
                price=e.get("price", 0),
                target=e.get("target"),
                timestamp=e.get("timestamp", ""),
            )
            for e in entries
        ]
        total += len(entries)

    return StockAlertHistoryResponse(
        total_alerts=total, unique_tickers=len(raw_alerts), alerts=alerts
    )


@router.get("/watchlist", response_model=WatchlistResponse)
async def get_stock_watchlist():
    """Get stock tickers organised by sector."""
    from app.engines.stock_sniper.config.tickers import (
        WATCHLIST,
        TECHNOLOGY, FINANCE, HEALTHCARE, CONSUMER,
        ENERGY_INDUSTRIALS, STAPLES_MATERIALS, TECHNOLOGY_2,
        FINANCE_2, HEALTHCARE_2, CONSUMER_2, ENERGY_INDUSTRIALS_2,
        TELECOM_UTILITIES, REAL_ESTATE, TRANSPORTATION,
        MATERIALS_2, SEMICONDUCTORS,
    )

    sectors = {
        "Technology": TECHNOLOGY + TECHNOLOGY_2,
        "Finance": FINANCE + FINANCE_2,
        "Healthcare": HEALTHCARE + HEALTHCARE_2,
        "Consumer": CONSUMER + CONSUMER_2,
        "Energy/Industrials": ENERGY_INDUSTRIALS + ENERGY_INDUSTRIALS_2,
        "Staples/Materials": STAPLES_MATERIALS,
        "Telecom/Utilities": TELECOM_UTILITIES,
        "Real Estate": REAL_ESTATE,
        "Transportation": TRANSPORTATION,
        "Materials": MATERIALS_2,
        "Semiconductors": SEMICONDUCTORS,
    }

    return WatchlistResponse(total=len(WATCHLIST), sectors=sectors)


@router.post("/scan", response_model=ScanResultResponse)
async def trigger_stock_scan(scheduler: SchedulerService = Depends(get_scheduler)):
    """Trigger an immediate stock scan."""
    await scheduler._run_stock_scan()
    return ScanResultResponse(
        service="stock_sniper",
        triggered=True,
        message=f"Scan complete. {scheduler.stats.stock_last_signals} signals found.",
        timestamp=datetime.now(),
    )
