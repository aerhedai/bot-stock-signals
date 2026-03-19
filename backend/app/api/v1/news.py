"""News feed API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends

from app.dependencies import get_scheduler, get_alert_store
from app.models.common import ScanResultResponse
from app.models.news import NewsFeedResponse, NewsArticleResponse, TickerNewsFeedResponse
from app.services.scheduler import SchedulerService

router = APIRouter(prefix="/news", tags=["news"])


@router.get("/feed", response_model=NewsFeedResponse)
async def get_news_feed(store=Depends(get_alert_store)):
    """Get recent news articles from history."""
    data = store.get_news_history()
    raw_news = data.get("news", {})

    articles = []
    stock_count = 0
    crypto_count = 0

    for news_id, entry in raw_news.items():
        cat = entry.get("category", "general")
        if cat == "stock":
            stock_count += 1
        elif cat == "crypto":
            crypto_count += 1

        articles.append(
            NewsArticleResponse(
                id=news_id,
                headline=entry.get("headline", ""),
                summary="",
                source="",
                url=entry.get("url", ""),
                category=cat,
                sent_at=entry.get("sent_at", ""),
                ticker=entry.get("ticker"),
            )
        )

    # Sort by sent_at descending
    articles.sort(key=lambda a: a.sent_at, reverse=True)

    return NewsFeedResponse(
        total=len(articles),
        stock_count=stock_count,
        crypto_count=crypto_count,
        articles=articles[:100],
    )


@router.get("/ticker/{ticker}", response_model=TickerNewsFeedResponse)
async def get_ticker_news(ticker: str):
    """
    Get recent news articles for a specific stock ticker (last 14 days).

    Checks stored history first. If fewer than 3 articles are found, fetches
    live from Finnhub and stores the results so subsequent calls are instant.
    """
    import asyncio
    from app.engines.news_monitor.config import config
    from app.engines.news_monitor.history import NewsHistory
    from app.engines.news_monitor.fetcher import NewsFetcher

    upper = ticker.upper()
    history = NewsHistory(str(config.NEWS_HISTORY_FILE))
    raw = history.get_ticker_history(upper, limit=20)

    if len(raw) < 3:
        # Nothing useful cached — fetch live from Finnhub and store
        fetcher = NewsFetcher()
        live = await asyncio.to_thread(fetcher.fetch_company_news, upper, 15)
        for article in live:
            if not history.is_sent(article.id):
                history.mark_sent(
                    news_id=article.id,
                    category="stock",
                    headline=article.headline,
                    url=article.url,
                    ticker=upper,
                )
        raw = history.get_ticker_history(upper, limit=20)

    articles = [
        NewsArticleResponse(
            id=entry.get("id", ""),
            headline=entry.get("headline", ""),
            summary="",
            source=entry.get("source", ""),
            url=entry.get("url", "") or "",
            category="stock",
            sent_at=entry.get("sent_at", ""),
            ticker=upper,
        )
        for entry in raw
    ]

    return TickerNewsFeedResponse(
        ticker=upper,
        total=len(articles),
        articles=articles,
    )


@router.post("/fetch", response_model=ScanResultResponse)
async def trigger_news_fetch(scheduler: SchedulerService = Depends(get_scheduler)):
    """Trigger an immediate news fetch."""
    await scheduler._run_news_fetch()
    return ScanResultResponse(
        service="news_monitor",
        triggered=True,
        message=f"Fetch complete. {scheduler.stats.news_last_articles} new articles.",
        timestamp=datetime.now(),
    )
