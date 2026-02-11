"""Pydantic models for crypto-related API responses."""

from pydantic import BaseModel
from typing import Optional


class CryptoSignalResponse(BaseModel):
    symbol: str
    name: str
    category: str
    current_price: float
    valuation_method: str
    valuation_score: float
    trigger_type: str
    severity: str
    combined_score: float
    timestamp: str


class CryptoWatchlistResponse(BaseModel):
    total: int
    categories: dict[str, list[str]]


class CryptoAlertHistoryResponse(BaseModel):
    total_alerts: int
    alerts: dict[str, str]  # symbol -> last alert timestamp
