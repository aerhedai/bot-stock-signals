"""
Dashboard orchestrator.

Drives the agent-powered dashboard endpoint. On each call it:

1. Runs an agentic task that reads cached signals, news, and market analysis.
2. Allows the agent to refresh stale analysis summaries via the existing
   update_market_analysis tool (registered by MarketAnalyzer).
3. Assembles a fully-typed DashboardResponse from the caches once the
   agent has finished — the structured data never depends on parsing
   the agent's free-text output.

Registers two additional tools that are exclusive to the dashboard context:
  - get_stock_signals  — recent stock sniper alerts from the alert store.
  - get_crypto_signals — recent crypto sniper alerts from the alert store.

The three market analysis tools (get_market_headlines, get_market_analysis,
update_market_analysis) are already registered by MarketAnalyzer and are
reused here via the shared AgentOrchestrator singleton.
"""

import logging
from datetime import datetime
from typing import Optional

from app.engines.market_analysis.analyzer import MarketAnalysisResult, get_analyzer
from app.models.analysis import MarketAnalysisResponse
from app.models.dashboard import (
    DashboardCryptoSignal,
    DashboardNewsItem,
    DashboardResponse,
    DashboardStockSignal,
)
from app.services import alert_store
from app.services.agent_orchestrator import get_orchestrator
from app.services.ai_service import AgentTool

logger = logging.getLogger(__name__)

# Maximum recent signals and news items to include in the response.
_MAX_SIGNALS = 10
_MAX_NEWS = 10

_AGENT_TASK = """\
You are preparing a real-time financial dashboard summary.

Steps:
1. Call get_stock_signals() and get_crypto_signals() to read the most recent alerts.
2. Call get_market_headlines(category='stock') and get_market_headlines(category='crypto') \
to see the current news pool.
3. Call get_market_analysis(category='stock') and get_market_analysis(category='crypto') \
to read the existing summaries.
4. For each category: if the existing analysis is absent, or was generated more than 3 hours ago, \
or its headline_count is significantly lower than the headlines now available — call \
update_market_analysis with a fresh 5-7 sentence summary covering key themes, sentiment, \
and risks. No price predictions.
5. Reply in 2-3 sentences: the current overall market picture (stocks and crypto combined), \
any signals or themes worth noting, and whether any analysis was refreshed.\
"""

_TOOL_NAMES = [
    "get_stock_signals",
    "get_crypto_signals",
    "get_market_headlines",
    "get_market_analysis",
    "update_market_analysis",
]


class DashboardOrchestrator:
    """
    Builds the dashboard payload using an agentic freshness check.

    Calling build_dashboard() runs the agent (which may refresh stale
    analysis), then assembles a DashboardResponse from deterministic
    cache reads — no parsing of the agent's text output is required
    for the structured data.
    """

    def __init__(self):
        # Ensure MarketAnalyzer is initialised so its three tools are
        # registered with the global orchestrator before we run any task.
        self._analyzer = get_analyzer()
        self._register_tools()

    # ------------------------------------------------------------------
    # Tool registration
    # ------------------------------------------------------------------

    def _register_tools(self):
        get_orchestrator().register_tools([
            AgentTool(
                name="get_stock_signals",
                description=(
                    "Read the most recent stock sniper signals from the alert store. "
                    "Returns the top 10 signals ordered by timestamp descending."
                ),
                parameters={"type": "object", "properties": {}},
                handler=self._tool_stock_signals,
            ),
            AgentTool(
                name="get_crypto_signals",
                description=(
                    "Read the most recent crypto sniper signals from the alert store. "
                    "Returns the top 10 signals ordered by timestamp descending."
                ),
                parameters={"type": "object", "properties": {}},
                handler=self._tool_crypto_signals,
            ),
        ])

    # ------------------------------------------------------------------
    # Tool handlers (synchronous — called by the agent loop)
    # ------------------------------------------------------------------

    def _tool_stock_signals(self) -> dict:
        data = alert_store.get_stock_alerts()
        raw = data.get("alerts", {})
        flat: list[dict] = []
        for ticker, entries in raw.items():
            if isinstance(entries, dict):
                entries = [entries]
            for e in entries:
                flat.append({
                    "ticker": ticker,
                    "method": e.get("method", ""),
                    "score": e.get("score", 0),
                    "price": e.get("price", 0),
                    "timestamp": e.get("timestamp", ""),
                })
        flat.sort(key=lambda x: x["timestamp"], reverse=True)
        return {"total": len(flat), "recent": flat[:_MAX_SIGNALS]}

    def _tool_crypto_signals(self) -> dict:
        data = alert_store.get_crypto_alerts()
        raw = data.get("alerts", {})
        signals = [
            {"symbol": symbol, "timestamp": entry.get("timestamp", "")}
            for symbol, entry in raw.items()
        ]
        signals.sort(key=lambda x: x["timestamp"], reverse=True)
        return {"total": len(signals), "recent": signals[:_MAX_SIGNALS]}

    # ------------------------------------------------------------------
    # Response assembly helpers
    # ------------------------------------------------------------------

    def _build_stock_signals(self) -> list[DashboardStockSignal]:
        data = alert_store.get_stock_alerts()
        raw = data.get("alerts", {})
        flat: list[DashboardStockSignal] = []
        for ticker, entries in raw.items():
            if isinstance(entries, dict):
                entries = [entries]
            for e in entries:
                flat.append(DashboardStockSignal(
                    ticker=ticker,
                    method=e.get("method", ""),
                    score=e.get("score", 0),
                    price=e.get("price", 0),
                    target=e.get("target"),
                    timestamp=e.get("timestamp", ""),
                ))
        flat.sort(key=lambda x: x.timestamp, reverse=True)
        return flat[:_MAX_SIGNALS]

    def _build_crypto_signals(self) -> list[DashboardCryptoSignal]:
        data = alert_store.get_crypto_alerts()
        raw = data.get("alerts", {})
        signals = [
            DashboardCryptoSignal(symbol=symbol, timestamp=entry.get("timestamp", ""))
            for symbol, entry in raw.items()
        ]
        signals.sort(key=lambda x: x.timestamp, reverse=True)
        return signals[:_MAX_SIGNALS]

    def _build_news(self) -> list[DashboardNewsItem]:
        raw = alert_store.get_news_history()
        items = [
            DashboardNewsItem(
                headline=v.get("headline", ""),
                category=v.get("category", ""),
                sent_at=v.get("sent_at", ""),
                url=v.get("url", ""),
            )
            for v in raw.get("news", {}).values()
        ]
        items.sort(key=lambda x: x.sent_at, reverse=True)
        return items[:_MAX_NEWS]

    @staticmethod
    def _analysis_to_response(
        result: Optional[MarketAnalysisResult],
        category_label: str,
    ) -> Optional[MarketAnalysisResponse]:
        if result is None:
            return None
        return MarketAnalysisResponse(
            category=category_label,
            analysis=result.analysis,
            headline_count=result.headline_count,
            generated_at=result.generated_at,
        )

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    async def build_dashboard(self) -> DashboardResponse:
        """
        Run the agent freshness check then assemble the full dashboard payload.

        The agent may update stale analysis summaries as a side effect.
        The structured response is always built from deterministic cache reads
        so it is never dependent on parsing the agent's free-text output.
        """
        reasoning = await get_orchestrator().run_task(
            _AGENT_TASK,
            tool_names=_TOOL_NAMES,
            temperature=0.2,
            max_turns=10,
        )

        return DashboardResponse(
            generated_at=datetime.now(),
            agent_reasoning=reasoning or "Dashboard assembled.",
            stock_signals=self._build_stock_signals(),
            crypto_signals=self._build_crypto_signals(),
            news=self._build_news(),
            stock_analysis=self._analysis_to_response(
                self._analyzer.get_cached("stock"), "stocks"
            ),
            crypto_analysis=self._analysis_to_response(
                self._analyzer.get_cached("crypto"), "crypto"
            ),
        )


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_instance: Optional[DashboardOrchestrator] = None


def get_dashboard_orchestrator() -> DashboardOrchestrator:
    """Return the shared DashboardOrchestrator instance, creating it on first call."""
    global _instance
    if _instance is None:
        _instance = DashboardOrchestrator()
    return _instance
