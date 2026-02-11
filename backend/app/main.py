"""
FastAPI application factory with lifespan management.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.dependencies import get_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start/stop the scheduler on app startup/shutdown."""
    scheduler = get_scheduler()
    scheduler.start()
    yield
    scheduler.stop()


app = FastAPI(
    title="Telegram Signals API",
    description="Backend API for stock, crypto, and news signal monitoring",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
