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
    fair_value_estimate: Optional[float] = None
    discount_percentage: Optional[float] = None
    trigger_type: str
    trigger_description: str = ""
    rsi: Optional[float] = None
    bollinger_position: Optional[str] = None
    change_24h: Optional[float] = None
    change_7d: Optional[float] = None
    severity: str
    confidence: str = "medium"
    combined_score: float
    timestamp: str


class CryptoWatchlistResponse(BaseModel):
    total: int
    categories: dict[str, list[str]]


class CryptoAlertHistoryResponse(BaseModel):
    total_alerts: int
    alerts: dict[str, CryptoSignalResponse]
