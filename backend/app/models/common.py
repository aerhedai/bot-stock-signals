"""Common Pydantic response models."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class HealthResponse(BaseModel):
    status: str = "ok"
    timestamp: datetime


class ServiceStatus(BaseModel):
    name: str
    running: bool
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    total_runs: int = 0


class ServiceStatusResponse(BaseModel):
    status: str = "ok"
    timestamp: datetime
    services: list[ServiceStatus]


class ScanResultResponse(BaseModel):
    service: str
    triggered: bool
    message: str
    timestamp: datetime
