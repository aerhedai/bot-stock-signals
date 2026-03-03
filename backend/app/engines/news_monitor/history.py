"""
News History Module

Tracks sent news articles to avoid sending duplicates.
Uses JSON-based storage with automatic cleanup of old entries.
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Set, Optional

logger = logging.getLogger(__name__)


class NewsHistory:
    """
    Manages history of sent news articles.

    Prevents duplicate news from being sent and automatically
    cleans up old entries (default: 7 days).
    """

    def __init__(self, db_path: str, retention_days: int = 7):
        """
        Initialise news history manager.

        Args:
            db_path: Path to JSON database file
            retention_days: Number of days to keep history
        """
        self.db_path = Path(db_path)
        self.retention_days = retention_days
        self.sent_ids: Set[str] = set()
        self.history: Dict[str, dict] = {}
        self._load_history()

    def _load_history(self):
        """Load news history from JSON file."""
        if self.db_path.exists():
            try:
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.history = data.get('news', {})
                    self.sent_ids = set(self.history.keys())

                # Clean up old entries
                self._cleanup_old_entries()

                logger.info(f"Loaded {len(self.sent_ids)} news articles from history")
            except Exception as e:
                logger.error(f"Error loading news history: {e}")
                self.history = {}
                self.sent_ids = set()
        else:
            logger.info(f"No existing news history found at {self.db_path}")
            self.history = {}
            self.sent_ids = set()

    def _save_history(self):
        """Save news history to JSON file."""
        try:
            # Ensure directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

            with open(self.db_path, 'w') as f:
                json.dump({
                    'news': self.history,
                    'last_updated': datetime.now().isoformat()
                }, f, indent=2)

            logger.debug(f"Saved news history to {self.db_path}")
        except Exception as e:
            logger.error(f"Error saving news history: {e}")

    def _cleanup_old_entries(self):
        """Remove entries older than retention period."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_days)
        old_count = len(self.history)

        # Filter out old entries
        self.history = {
            news_id: data
            for news_id, data in self.history.items()
            if datetime.fromisoformat(data['sent_at']) > cutoff_date
        }

        self.sent_ids = set(self.history.keys())

        removed = old_count - len(self.history)
        if removed > 0:
            logger.info(f"Cleaned up {removed} old news entries")
            self._save_history()

    def is_sent(self, news_id: str) -> bool:
        """
        Check if a news article has been sent.

        Args:
            news_id: Unique identifier for the news article

        Returns:
            True if already sent, False otherwise
        """
        return news_id in self.sent_ids

    def mark_sent(self, news_id: str, category: str, headline: str, url: Optional[str] = None):
        """
        Mark a news article as sent.

        Args:
            news_id: Unique identifier for the news article
            category: Category (stock or crypto)
            headline: News headline
            url: Optional URL to the article
        """
        self.history[news_id] = {
            'sent_at': datetime.now().isoformat(),
            'category': category,
            'headline': headline,
            'url': url
        }
        self.sent_ids.add(news_id)
        self._save_history()

        logger.debug(f"Marked news as sent: {news_id[:50]}")

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about sent news."""
        stats = {
            'total': len(self.history),
            'stock': 0,
            'crypto': 0,
            'other': 0
        }

        for data in self.history.values():
            category = data.get('category', 'other')
            stats[category] = stats.get(category, 0) + 1

        return stats

    def clear_all(self):
        """Clear all history (use with caution)."""
        self.history = {}
        self.sent_ids = set()
        self._save_history()
        logger.warning("All news history cleared")
