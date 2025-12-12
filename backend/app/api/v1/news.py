"""News feed API endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends

from app.dependencies import get_scheduler, get_alert_store
from app.models.common import ScanResultResponse
from app.models.news import NewsFeedResponse, NewsArticleResponse
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
            )
        )

    # Sort by sent_at descending
    articles.sort(key=lambda a: a.sent_at, reverse=True)

    return NewsFeedResponse(
        total=len(articles),
        stock_count=stock_count,
        crypto_count=crypto_count,
        articles=articles[:100],  # Limit to recent 100
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
