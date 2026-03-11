"""Agent-driven dashboard endpoint."""

from fastapi import APIRouter, HTTPException

from app.models.dashboard import DashboardResponse

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


def _get_orchestrator():
    # Deferred import keeps startup clean if Vertex AI credentials are absent.
    from app.engines.dashboard.orchestrator import get_dashboard_orchestrator
    return get_dashboard_orchestrator()


@router.get("", response_model=DashboardResponse)
async def get_dashboard():
    """
    Return a fully assembled dashboard payload in a single request.

    The agent checks whether cached market analysis summaries are stale
    relative to the current news pool and refreshes them if needed before
    returning. Stock signals, crypto signals, news, and analysis are all
    included in one response.
    """
    try:
        return await _get_orchestrator().build_dashboard()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
