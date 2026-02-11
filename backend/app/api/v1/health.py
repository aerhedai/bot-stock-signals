"""Health check endpoints."""

from datetime import datetime

from fastapi import APIRouter, Depends

from app.dependencies import get_scheduler
from app.models.common import HealthResponse, ServiceStatusResponse, ServiceStatus
from app.services.scheduler import SchedulerService

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
async def health_check():
    """Basic health check."""
    return HealthResponse(status="ok", timestamp=datetime.now())


@router.get("/status", response_model=ServiceStatusResponse)
async def detailed_status(scheduler: SchedulerService = Depends(get_scheduler)):
    """Detailed status with scheduler stats."""
    stats = scheduler.stats
    services = [
        ServiceStatus(
            name="stock_sniper",
            running=scheduler.is_running,
            last_run=stats.stock_last_run,
            next_run=scheduler.get_next_run("stock_scan"),
            total_runs=stats.stock_total_runs,
        ),
        ServiceStatus(
            name="crypto_sniper",
            running=scheduler.is_running,
            last_run=stats.crypto_last_run,
            next_run=scheduler.get_next_run("crypto_scan"),
            total_runs=stats.crypto_total_runs,
        ),
        ServiceStatus(
            name="news_monitor",
            running=scheduler.is_running,
            last_run=stats.news_last_run,
            next_run=scheduler.get_next_run("news_fetch"),
            total_runs=stats.news_total_runs,
        ),
    ]
    return ServiceStatusResponse(
        status="ok", timestamp=datetime.now(), services=services
    )
