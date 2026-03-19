"""Market analysis API endpoints."""

from fastapi import APIRouter, HTTPException

from app.models.analysis import AnalysisTriggerResponse, MarketAnalysisResponse

router = APIRouter(prefix="/analysis", tags=["analysis"])


def _get_analyzer():
    # Deferred import keeps startup clean if Vertex AI credentials are absent.
    from app.engines.market_analysis.analyzer import get_analyzer
    return get_analyzer()


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
        stock_reasoning, crypto_reasoning = await _get_analyzer().run_all()
        return AnalysisTriggerResponse(
            triggered=True,
            message="Market analysis agent completed.",
            stocks_reasoning=stock_reasoning,
            crypto_reasoning=crypto_reasoning,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
