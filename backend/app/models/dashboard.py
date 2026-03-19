"""Pydantic models for the agent-driven dashboard API response."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel

from app.models.analysis import MarketAnalysisResponse


class DashboardStockSignal(BaseModel):
    ticker: str
    method: str
    score: float
    price: float
    target: Optional[float] = None
    timestamp: str


class DashboardCryptoSignal(BaseModel):
    symbol: str
    timestamp: str


class DashboardNewsItem(BaseModel):
    headline: str
    category: str
    sent_at: str
    url: str


class DashboardResponse(BaseModel):
    generated_at: datetime
    agent_reasoning: str
    stock_signals: list[DashboardStockSignal]
    crypto_signals: list[DashboardCryptoSignal]
    news: list[DashboardNewsItem]
    stock_analysis: Optional[MarketAnalysisResponse] = None
    crypto_analysis: Optional[MarketAnalysisResponse] = None
