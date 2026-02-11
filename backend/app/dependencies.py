"""
FastAPI dependency injection providers.
"""

from __future__ import annotations

from typing import Optional

from app.services.scheduler import SchedulerService
from app.services import alert_store

# Singleton scheduler instance
_scheduler: Optional[SchedulerService] = None


def get_scheduler() -> SchedulerService:
    """Get the global scheduler instance."""
    global _scheduler
    if _scheduler is None:
        _scheduler = SchedulerService()
    return _scheduler


def get_alert_store():
    """Get the alert store module."""
    return alert_store
