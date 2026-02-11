"""
News Formatter Module

Formats news articles for Telegram messages with proper HTML formatting.
"""

import logging
from typing import List
from datetime import datetime

from app.engines.news_monitor.fetcher import NewsArticle

logger = logging.getLogger(__name__)


class NewsFormatter:
    """Formats news articles for Telegram."""

    @staticmethod
    def format_article(article: NewsArticle, include_summary: bool = True) -> str:
        """
        Format a single news article for Telegram.

        Args:
            article: NewsArticle object to format
            include_summary: Whether to include the summary

        Returns:
            Formatted HTML message
        """
        lines = []

        # Category emoji
        emoji = "📈" if article.category == "stock" else "₿" if article.category == "crypto" else "📰"

        # Header with headline
        lines.append(f"{emoji} <b>{article.headline}</b>")
        lines.append("")

        # Summary (if available and requested)
        if include_summary and article.summary:
            # Truncate summary if too long
            summary = article.summary
            if len(summary) > 300:
                summary = summary[:297] + "..."
            lines.append(summary)
            lines.append("")

        # Metadata
        time_ago = NewsFormatter._time_ago(article.published_at)
        lines.append(f"🕐 <i>{time_ago}</i> • 📡 {article.source}")

        # Related symbols
        if article.related_symbols:
            symbols_str = ", ".join(article.related_symbols[:5])
            lines.append(f"🏷 {symbols_str}")

        # URL
        if article.url:
            lines.append(f"🔗 <a href='{article.url}'>Read more</a>")

        return "\n".join(lines)

    @staticmethod
    def format_multiple(articles: List[NewsArticle], max_articles: int = 5) -> List[str]:
        """
        Format multiple articles into separate messages.

        Args:
            articles: List of NewsArticle objects
            max_articles: Maximum number of articles to format

        Returns:
            List of formatted message strings
        """
        messages = []

        for article in articles[:max_articles]:
            message = NewsFormatter.format_article(article, include_summary=True)
            messages.append(message)

        return messages

    @staticmethod
    def format_digest(articles: List[NewsArticle], category: str = "Financial") -> str:
        """
        Format multiple articles as a digest (single message).

        Args:
            articles: List of NewsArticle objects
            category: Category name for the digest header

        Returns:
            Single formatted message with multiple articles
        """
        if not articles:
            return f"ℹ️ <b>No new {category.lower()} news at this time.</b>"

        lines = []

        # Header
        emoji = "📈" if category.lower() == "stock" else "₿" if category.lower() == "crypto" else "📰"
        lines.append(f"{emoji} <b>{category} News Digest</b>")
        lines.append(f"<i>{datetime.now().strftime('%B %d, %Y - %H:%M')}</i>")
        lines.append("=" * 40)
        lines.append("")

        # Articles (max 5 for digest)
        for i, article in enumerate(articles[:5], 1):
            time_ago = NewsFormatter._time_ago(article.published_at)

            lines.append(f"<b>{i}. {article.headline}</b>")
            lines.append(f"   🕐 {time_ago} • 📡 {article.source}")

            if article.url:
                lines.append(f"   🔗 <a href='{article.url}'>Read more</a>")

            lines.append("")

        # Footer
        lines.append("=" * 40)
        lines.append(f"<i>Total: {len(articles)} articles</i>")

        return "\n".join(lines)

    @staticmethod
    def _time_ago(published_at: datetime) -> str:
        """
        Get human-readable time difference.

        Args:
            published_at: Publication datetime

        Returns:
            Human-readable time string (e.g., "2 hours ago")
        """
        now = datetime.now()
        diff = now - published_at

        if diff.days > 0:
            if diff.days == 1:
                return "1 day ago"
            return f"{diff.days} days ago"

        hours = diff.seconds // 3600
        if hours > 0:
            if hours == 1:
                return "1 hour ago"
            return f"{hours} hours ago"

        minutes = diff.seconds // 60
        if minutes > 0:
            if minutes == 1:
                return "1 minute ago"
            return f"{minutes} minutes ago"

        return "just now"

    @staticmethod
    def format_error(error_message: str) -> str:
        """Format an error message."""
        return f"❌ <b>News Monitor Error</b>\n\n{error_message}"

    @staticmethod
    def format_status(message: str) -> str:
        """Format a status update message."""
        return f"ℹ️ <b>News Monitor Status</b>\n\n{message}"


if __name__ == '__main__':
    # Test the formatter
    from datetime import timedelta

    print("Testing News Formatter")
    print("=" * 60)

    # Create test article
    test_article = NewsArticle(
        id="test-1",
        headline="Bitcoin Surges Past $50,000 as Institutional Interest Grows",
        summary="Bitcoin has reached a new milestone, crossing the $50,000 mark amid growing institutional adoption and positive regulatory developments.",
        source="CryptoNews",
        url="https://example.com/bitcoin-news",
        published_at=datetime.now() - timedelta(hours=2),
        category="crypto",
        related_symbols=["BTC", "BTCUSD"]
    )

    # Test single article formatting
    print("\nSingle Article Format:")
    print("-" * 60)
    formatted = NewsFormatter.format_article(test_article)
    print(formatted)

    # Test digest formatting
    print("\n\nDigest Format:")
    print("-" * 60)
    articles = [test_article, test_article, test_article]
    digest = NewsFormatter.format_digest(articles, category="Crypto")
    print(digest)
