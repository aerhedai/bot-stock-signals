"""Pydantic models for news-related API responses."""

from pydantic import BaseModel
from typing import Optional


class NewsArticleResponse(BaseModel):
    id: str
    headline: str
    summary: str
    source: str
    url: str
    category: str
    sent_at: str
    ticker: Optional[str] = None


class NewsFeedResponse(BaseModel):
    total: int
    stock_count: int
    crypto_count: int
    articles: list[NewsArticleResponse]


class TickerNewsFeedResponse(BaseModel):
    ticker: str
    total: int
    articles: list[NewsArticleResponse]
