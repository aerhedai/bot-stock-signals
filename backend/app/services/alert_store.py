"""
Unified read/write for JSON alert files across all engine modules.
"""

import json
import logging
from datetime import datetime, timedelta
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


def _write_json(path: Path, data: dict[str, Any]) -> None:
    """Write a dict to a JSON file, creating parent directories as needed."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        logger.error(f"Error writing {path}: {e}")


def get_stock_alerts() -> dict[str, Any]:
    """Read stock alert history from JSON."""
    return _read_json(_STOCK_ALERTS)


def save_stock_alerts(alerts: dict[str, Any]) -> None:
    """Persist stock alerts to JSON (overwrites the file)."""
    _write_json(_STOCK_ALERTS, {
        "alerts": alerts,
        "last_updated": datetime.now().isoformat(),
    })


def get_crypto_alerts() -> dict[str, Any]:
    """Read crypto alert history from JSON."""
    return _read_json(_CRYPTO_ALERTS)


def save_crypto_alerts(alerts: dict[str, Any]) -> None:
    """Persist crypto alerts to JSON (overwrites the file)."""
    _write_json(_CRYPTO_ALERTS, {
        "alerts": alerts,
        "last_updated": datetime.now().isoformat(),
    })


def get_news_history() -> dict[str, Any]:
    """Read news history from JSON."""
    return _read_json(_NEWS_HISTORY)


def get_recent_signal_tickers(days: int = 30) -> list[str]:
    """
    Return unique stock tickers that have fired a signal within the last `days` days.

    Used by the ticker news fetcher to know which companies to pull news for.
    """
    cutoff = datetime.now() - timedelta(days=days)
    raw = _read_json(_STOCK_ALERTS).get("alerts", {})
    tickers: list[str] = []
    for ticker, entries in raw.items():
        if isinstance(entries, dict):
            entries = [entries]
        for entry in entries:
            ts_str = entry.get("timestamp", "")
            try:
                if datetime.fromisoformat(ts_str) >= cutoff:
                    tickers.append(ticker)
                    break
            except ValueError:
                pass
    return tickers
