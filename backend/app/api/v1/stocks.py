"""Stock signal API endpoints."""

import asyncio
from datetime import datetime
from math import isnan

import pandas as pd
import yfinance as yf
from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_scheduler, get_alert_store
from app.models.common import ScanResultResponse
from app.models.stocks import (
    StockAlertHistoryResponse, StockSignalResponse, WatchlistResponse,
    StockChartResponse, StockChartPoint, AiInsightResponse,
)
from app.services.scheduler import SchedulerService

router = APIRouter(prefix="/stocks", tags=["stocks"])


@router.get("/signals", response_model=StockAlertHistoryResponse)
async def get_stock_signals(store=Depends(get_alert_store)):
    """Get the latest stock prediction per ticker."""
    data = store.get_stock_alerts()
    raw_alerts = data.get("alerts", {})

    alerts: dict[str, StockSignalResponse] = {}
    for ticker, entry in raw_alerts.items():
        # Support old list format — take the most recent entry
        if isinstance(entry, list):
            if not entry:
                continue
            entry = entry[-1]

        alerts[ticker] = StockSignalResponse(
            ticker=ticker,
            method=entry.get("method", ""),
            time_horizon=entry.get("time_horizon", ""),
            score=entry.get("score", 0),
            price=entry.get("price", 0),
            target=entry.get("target"),
            reason=entry.get("reason", ""),
            ema_value=entry.get("ema_value"),
            timestamp=entry.get("timestamp", ""),
        )

    return StockAlertHistoryResponse(
        total_alerts=len(alerts),
        unique_tickers=len(alerts),
        alerts=alerts,
    )


@router.get("/chart/{ticker}", response_model=StockChartResponse)
async def get_stock_chart(ticker: str, store=Depends(get_alert_store)):
    """Return 60 days of daily price + EMA-20 data for a ticker."""
    def _fetch():
        hist = yf.Ticker(ticker).history(period="60d", interval="1d")
        if hist.empty:
            return None
        closes = hist["Close"]
        ema20 = closes.ewm(span=20, adjust=False).mean()
        points = []
        for date, price, ema in zip(hist.index, closes, ema20):
            points.append(StockChartPoint(
                date=date.strftime("%Y-%m-%d"),
                price=round(float(price), 4),
                ema20=None if isnan(float(ema)) else round(float(ema), 4),
            ))
        return points

    points = await asyncio.to_thread(_fetch)
    if points is None:
        raise HTTPException(status_code=404, detail=f"No data found for {ticker}")

    # Pull signal metadata from the alert store
    raw_alerts = store.get_stock_alerts().get("alerts", {})
    entry = raw_alerts.get(ticker)
    if isinstance(entry, list):
        entry = entry[-1] if entry else None

    target_price = entry.get("target") if entry else None
    signal_date = entry.get("timestamp", "")[:10] if entry else None
    signal_price = entry.get("price") if entry else None

    return StockChartResponse(
        ticker=ticker,
        data=points,
        target_price=target_price,
        signal_date=signal_date,
        signal_price=signal_price,
    )


@router.get("/ai-insight/{ticker}", response_model=AiInsightResponse)
async def get_stock_ai_insight(ticker: str, store=Depends(get_alert_store)):
    """Generate an AI-powered insight for a stock ticker based on signal data and recent news."""
    from app.services.ai_service import get_ai_service
    from app.services import alert_store as store_svc

    raw_alerts = store.get_stock_alerts().get("alerts", {})
    entry = raw_alerts.get(ticker)
    if isinstance(entry, list):
        entry = entry[-1] if entry else None

    if not entry:
        raise HTTPException(status_code=404, detail=f"No signal found for {ticker}")

    # Gather relevant news headlines
    news_data = store_svc.get_news_history()
    all_articles = list(news_data.get("news", {}).values())
    ticker_lower = ticker.lower()
    related = [
        a["headline"] for a in all_articles
        if isinstance(a, dict) and ticker_lower in a.get("headline", "").lower()
    ][:5]

    news_section = "\n".join(f"- {h}" for h in related) if related else "No recent news found for this ticker."

    prompt = (
        f"You are a financial analyst providing a concise insight for a trading signal.\n\n"
        f"Ticker: {ticker}\n"
        f"Valuation method: {entry.get('method', 'N/A')}\n"
        f"Signal score: {entry.get('score', 'N/A')}/100\n"
        f"Entry price: ${entry.get('price', 'N/A')}\n"
        f"Target price: ${entry.get('target', 'N/A')}\n"
        f"Time horizon: {entry.get('time_horizon', 'N/A')}\n"
        f"Reason: {entry.get('reason', 'N/A')}\n\n"
        f"Related recent news headlines:\n{news_section}\n\n"
        f"Write 3-4 sentences covering: (1) why this ticker is interesting right now based on the signal, "
        f"(2) any relevant catalysts or risks from the news, (3) what to watch for. "
        f"Be specific and actionable. Do not repeat the raw numbers already shown in the UI."
    )

    ai = get_ai_service()
    insight = await ai.generate(prompt, temperature=0.5, max_tokens=300)

    return AiInsightResponse(
        ticker=ticker,
        insight=insight,
        generated_at=datetime.now().isoformat(),
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
