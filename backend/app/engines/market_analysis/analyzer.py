"""
MarketAnalyzer — generates AI market summaries from recent news headlines.

Reads from the news monitor's history file, groups headlines by category,
and calls AIService.generate() using shared prompt templates.
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

from app.services.ai_service import PROMPT_TEMPLATES, get_ai_service

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
    """

    def __init__(self, news_history_path: Optional[Path] = None):
        self._news_path = news_history_path or _NEWS_HISTORY_PATH
        self._cache: dict[str, MarketAnalysisResult] = {}
        self._load_cache()

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
    # Analysis generation
    # ------------------------------------------------------------------

    async def analyze(self, category: str) -> Optional[MarketAnalysisResult]:
        """
        Generate fresh AI analysis for 'stock' or 'crypto'.

        Returns the cached result if there are no headlines to analyse.
        Returns None if there are no headlines and no cached result.
        """
        headlines = self._get_recent_headlines(category)
        if not headlines:
            logger.info("No recent %s headlines — returning cached result", category)
            return self._cache.get(category)

        template_key = f"market_analysis_{'stocks' if category == 'stock' else 'crypto'}"
        prompt = PROMPT_TEMPLATES[template_key].format(
            headlines="\n".join(f"- {h}" for h in headlines)
        )

        ai = get_ai_service()
        text = await ai.generate(prompt, temperature=0.5, max_tokens=1024)

        result = MarketAnalysisResult(
            category=category,
            analysis=text,
            headline_count=len(headlines),
        )
        self._cache[category] = result
        self._save_cache()

        logger.info(
            "Generated %s analysis from %d headlines", category, len(headlines)
        )
        return result

    async def run_all(self):
        """Analyse stocks and crypto in parallel."""
        await asyncio.gather(self.analyze("stock"), self.analyze("crypto"))

    def get_cached(self, category: str) -> Optional[MarketAnalysisResult]:
        """Return the latest cached result without triggering generation."""
        return self._cache.get(category)
