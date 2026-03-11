"""Pydantic models for market analysis API responses."""

from datetime import datetime

from pydantic import BaseModel


class MarketAnalysisResponse(BaseModel):
    category: str
    analysis: str
    headline_count: int
    generated_at: datetime


class AnalysisTriggerResponse(BaseModel):
    triggered: bool
    message: str
    stocks_reasoning: str = ""
    crypto_reasoning: str = ""
