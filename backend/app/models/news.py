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


class NewsFeedResponse(BaseModel):
    total: int
    stock_count: int
    crypto_count: int
    articles: list[NewsArticleResponse]
