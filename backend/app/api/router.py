"""Aggregates all v1 API routes."""

from fastapi import APIRouter

from app.api.v1 import health, stocks, crypto, news

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(stocks.router)
api_router.include_router(crypto.router)
api_router.include_router(news.router)
