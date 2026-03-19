"""Aggregates all v1 API routes."""

from fastapi import APIRouter

from app.api.v1 import analysis, dashboard, health, stocks, crypto, news

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health.router)
api_router.include_router(stocks.router)
api_router.include_router(crypto.router)
api_router.include_router(news.router)
api_router.include_router(analysis.router)
api_router.include_router(dashboard.router)
