"""
MarketAnalyzer — generates AI market summaries from recent news headlines.

Reads from the news monitor's history file, groups headlines by category,
and uses the AgentOrchestrator to decide whether a fresh summary is needed.
Results are cached in memory and persisted to a local JSON file so the
last analysis survives a server restart.
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from app.services.ai_service import AgentTool
from app.services.agent_orchestrator import get_orchestrator

logger = logging.getLogger(__name__)

_NEWS_HISTORY_PATH = (
    Path(__file__).resolve().parent.parent / "news_monitor" / "data" / "news_history.json"
)
_CACHE_FILE = Path(__file__).parent / "data" / "analysis_cache.json"


@dataclass
class MarketAnalysisResult:
    category: str          # 'stock' or 'crypto'
    analysis: str
    headline_count: int
    generated_at: datetime = field(default_factory=datetime.now)


class MarketAnalyzer:
    """
    Generates AI-written market summaries using recent news headlines.

    Categories map to the two sides of the news feed: 'stock' and 'crypto'.
    Analysis is triggered on a schedule via the scheduler, and also available
    on-demand through the POST /api/v1/analysis/trigger endpoint.

    Uses the AgentOrchestrator so the agent decides whether to update the
    cached summary rather than blindly regenerating it on every call.
    """

    def __init__(self, news_history_path: Optional[Path] = None):
        self._news_path = news_history_path or _NEWS_HISTORY_PATH
        self._cache: dict[str, MarketAnalysisResult] = {}
        self._load_cache()
        self._register_tools()

    # ------------------------------------------------------------------
    # Cache persistence
    # ------------------------------------------------------------------

    def _load_cache(self):
        if not _CACHE_FILE.exists():
            return
        try:
            with open(_CACHE_FILE) as f:
                data = json.load(f)
            for cat, entry in data.items():
                self._cache[cat] = MarketAnalysisResult(
                    category=cat,
                    analysis=entry["analysis"],
                    headline_count=entry["headline_count"],
                    generated_at=datetime.fromisoformat(entry["generated_at"]),
                )
            logger.debug("Loaded analysis cache (%d entries)", len(self._cache))
        except Exception as e:
            logger.warning("Could not load analysis cache: %s", e)

    def _save_cache(self):
        _CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {
            cat: {
                "analysis": r.analysis,
                "headline_count": r.headline_count,
                "generated_at": r.generated_at.isoformat(),
            }
            for cat, r in self._cache.items()
        }
        with open(_CACHE_FILE, "w") as f:
            json.dump(data, f, indent=2)

    # ------------------------------------------------------------------
    # News headline retrieval
    # ------------------------------------------------------------------

    def _get_recent_headlines(
        self, category: str, max_age_hours: int = 24, limit: int = 30
    ) -> list[str]:
        """Pull the most recent headlines for a category from news history."""
        try:
            with open(self._news_path) as f:
                raw = json.load(f)
            news = raw.get("news", {})
            cutoff = datetime.now() - timedelta(hours=max_age_hours)

            headlines = [
                entry["headline"]
                for entry in news.values()
                if entry.get("category") == category
                and datetime.fromisoformat(entry["sent_at"]) > cutoff
            ]
            # Return the most recent `limit` headlines
            return headlines[-limit:]
        except Exception as e:
            logger.warning("Could not read news history: %s", e)
            return []

    # ------------------------------------------------------------------
    # Agent tool registration
    # ------------------------------------------------------------------

    def _register_tools(self):
        get_orchestrator().register_tools([
            AgentTool(
                name="get_ticker_headlines",
                description=(
                    "Fetch recent news headlines for a specific stock ticker symbol "
                    "from the last 14 days. Use this to get company-specific context "
                    "when analysing a signal or building a market view."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "ticker": {
                            "type": "string",
                            "description": "Stock ticker symbol, e.g. 'AAPL' or 'MOS'.",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of headlines to return (default 10).",
                        },
                    },
                    "required": ["ticker"],
                },
                handler=self._tool_get_ticker_headlines,
            ),
            AgentTool(
                name="get_market_headlines",
                description="Fetch recent news headlines for 'stock' or 'crypto' category.",
                parameters={
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "enum": ["stock", "crypto"]},
                        "max_age_hours": {
                            "type": "integer",
                            "description": "Look-back window in hours (default 24).",
                        },
                    },
                    "required": ["category"],
                },
                handler=self._tool_get_headlines,
            ),
            AgentTool(
                name="get_market_analysis",
                description="Read the current cached market analysis for 'stock' or 'crypto'.",
                parameters={
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "enum": ["stock", "crypto"]},
                    },
                    "required": ["category"],
                },
                handler=self._tool_get_current_analysis,
            ),
            AgentTool(
                name="update_market_analysis",
                description=(
                    "Write a new market analysis to cache. Call only if the current analysis "
                    "is outdated or missing. 5-7 sentences, no price predictions."
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "category": {"type": "string", "enum": ["stock", "crypto"]},
                        "analysis": {"type": "string"},
                        "headline_count": {"type": "integer"},
                    },
                    "required": ["category", "analysis", "headline_count"],
                },
                handler=self._tool_update_analysis,
            ),
        ])

    # ------------------------------------------------------------------
    # Tool handlers (synchronous — called by the agent loop)
    # ------------------------------------------------------------------

    def _tool_get_ticker_headlines(self, ticker: str, limit: int = 10) -> dict:
        from app.engines.news_monitor.config import config
        from app.engines.news_monitor.history import NewsHistory

        history = NewsHistory(str(config.NEWS_HISTORY_FILE))
        articles = history.get_ticker_history(ticker.upper(), limit=limit)
        return {
            "ticker": ticker.upper(),
            "article_count": len(articles),
            "headlines": [a.get("headline", "") for a in articles],
        }

    def _tool_get_headlines(self, category: str, max_age_hours: int = 24) -> dict:
        headlines = self._get_recent_headlines(category, max_age_hours=max_age_hours)
        return {
            "category": category,
            "headline_count": len(headlines),
            "headlines": headlines,
        }

    def _tool_get_current_analysis(self, category: str) -> dict:
        cached = self._cache.get(category)
        if cached is None:
            return {"category": category, "exists": False, "analysis": None}
        return {
            "category": category,
            "exists": True,
            "analysis": cached.analysis,
            "headline_count": cached.headline_count,
            "generated_at": cached.generated_at.isoformat(),
        }

    def _tool_update_analysis(
        self, category: str, analysis: str, headline_count: int
    ) -> dict:
        result = MarketAnalysisResult(
            category=category,
            analysis=analysis,
            headline_count=headline_count,
        )
        self._cache[category] = result
        self._save_cache()
        logger.info(
            "Agent updated %s analysis (%d headlines)", category, headline_count
        )
        return {"success": True}

    # ------------------------------------------------------------------
    # Analysis generation
    # ------------------------------------------------------------------

    async def analyze(self, category: str) -> str:
        """
        Run the agent to decide whether the cached analysis needs updating.

        The agent reads the current headlines and cached summary, then either
        updates the cache via update_market_analysis or leaves it unchanged.
        Returns the agent's 1-2 sentence reasoning.
        """
        label = "stock market" if category == "stock" else "crypto market"
        task = (
            f"You are maintaining an up-to-date {label} analysis summary.\n\n"
            f"Steps:\n"
            f"1. Call get_market_headlines(category='{category}') to see available news.\n"
            f"2. Call get_market_analysis(category='{category}') to read the existing summary.\n"
            f"3. Decide: do the headlines include significant new developments not reflected "
            f"in the current analysis? (new regulatory events, major moves, sentiment shifts)\n"
            f"4. If yes — call update_market_analysis with a fresh 5-7 sentence summary "
            f"covering key themes, sentiment, and risks. No price predictions.\n"
            f"5. If no — do NOT call update_market_analysis.\n"
            f"6. Reply with 1-2 sentences: what you decided and why."
        )
        tool_names = ["get_market_headlines", "get_market_analysis", "update_market_analysis"]
        reasoning = await get_orchestrator().run_task(task, tool_names=tool_names)
        return reasoning or f"Agent completed {category} analysis."

    async def run_all(self) -> tuple[str, str]:
        """Analyse stocks and crypto in parallel. Returns agent reasoning for each."""
        return await asyncio.gather(self.analyze("stock"), self.analyze("crypto"))

    def get_cached(self, category: str) -> Optional[MarketAnalysisResult]:
        """Return the latest cached result without triggering generation."""
        return self._cache.get(category)


# ---------------------------------------------------------------------------
# Singleton
# ---------------------------------------------------------------------------

_instance: Optional[MarketAnalyzer] = None


def get_analyzer() -> MarketAnalyzer:
    """Return the shared MarketAnalyzer instance, creating it on first call."""
    global _instance
    if _instance is None:
        _instance = MarketAnalyzer()
    return _instance
