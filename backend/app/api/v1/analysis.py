"""Market analysis API endpoints."""

from datetime import datetime

from fastapi import APIRouter, HTTPException

from app.models.analysis import AnalysisTriggerResponse, MarketAnalysisResponse

router = APIRouter(prefix="/analysis", tags=["analysis"])

# Lazy singleton — avoids importing at module load time so the app starts
# cleanly even if Vertex AI credentials aren't configured yet.
_analyzer = None


def _get_analyzer():
    global _analyzer
    if _analyzer is None:
        from app.engines.market_analysis.analyzer import MarketAnalyzer
        _analyzer = MarketAnalyzer()
    return _analyzer


@router.get("/stocks", response_model=MarketAnalysisResponse)
async def get_stock_analysis():
    """Get the latest AI-generated stock market analysis."""
    result = _get_analyzer().get_cached("stock")
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No stock analysis yet. POST /api/v1/analysis/trigger to generate one.",
        )
    return MarketAnalysisResponse(
        category="stocks",
        analysis=result.analysis,
        headline_count=result.headline_count,
        generated_at=result.generated_at,
    )


@router.get("/crypto", response_model=MarketAnalysisResponse)
async def get_crypto_analysis():
    """Get the latest AI-generated crypto market analysis."""
    result = _get_analyzer().get_cached("crypto")
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No crypto analysis yet. POST /api/v1/analysis/trigger to generate one.",
        )
    return MarketAnalysisResponse(
        category="crypto",
        analysis=result.analysis,
        headline_count=result.headline_count,
        generated_at=result.generated_at,
    )


@router.post("/trigger", response_model=AnalysisTriggerResponse)
async def trigger_analysis():
    """Trigger fresh AI market analysis for both stocks and crypto."""
    try:
        await _get_analyzer().run_all()
        return AnalysisTriggerResponse(
            triggered=True,
            message="Market analysis updated for stocks and crypto.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
