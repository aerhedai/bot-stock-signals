"""Pydantic models for stock-related API responses."""

from pydantic import BaseModel
from typing import Optional


class StockSignalResponse(BaseModel):
    ticker: str
    method: str
    time_horizon: str
    score: float
    price: float
    target: Optional[float] = None
    reason: str = ""
    ema_value: Optional[float] = None
    timestamp: str


class WatchlistItem(BaseModel):
    ticker: str
    sector: str


class WatchlistResponse(BaseModel):
    total: int
    sectors: dict[str, list[str]]


class StockAlertHistoryResponse(BaseModel):
    total_alerts: int
    unique_tickers: int
    alerts: dict[str, StockSignalResponse]
