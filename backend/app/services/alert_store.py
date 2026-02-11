"""
Unified read/write for JSON alert files across all engine modules.
"""

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Data file paths relative to engines directory
_ENGINES_DIR = Path(__file__).resolve().parent.parent / "engines"
_STOCK_ALERTS = _ENGINES_DIR / "stock_sniper" / "data" / "alerts.json"
_CRYPTO_ALERTS = _ENGINES_DIR / "crypto_sniper" / "data" / "alerts.json"
_NEWS_HISTORY = _ENGINES_DIR / "news_monitor" / "data" / "news_history.json"


def _read_json(path: Path) -> dict[str, Any]:
    """Read a JSON file, returning empty dict if not found."""
    if not path.exists():
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error reading {path}: {e}")
        return {}


def get_stock_alerts() -> dict[str, Any]:
    """Read stock alert history from JSON."""
    return _read_json(_STOCK_ALERTS)


def get_crypto_alerts() -> dict[str, Any]:
    """Read crypto alert history from JSON."""
    return _read_json(_CRYPTO_ALERTS)


def get_news_history() -> dict[str, Any]:
    """Read news history from JSON."""
    return _read_json(_NEWS_HISTORY)
