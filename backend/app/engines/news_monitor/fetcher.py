"""
Finnhub News Fetcher

Fetches financial news from Finnhub API and categorizes as stock or crypto news.
"""

import logging
import requests
from typing import List, Dict, Optional
from datetime import datetime

from app.engines.news_monitor.config import config

logger = logging.getLogger(__name__)


class NewsArticle:
    """Represents a news article."""

    def __init__(
        self,
        id: str,
        headline: str,
        summary: str,
        source: str,
        url: str,
        published_at: datetime,
        category: str,
        related_symbols: List[str] = None,
        image_url: Optional[str] = None
    ):
        self.id = id
        self.headline = headline
        self.summary = summary
        self.source = source
        self.url = url
        self.published_at = published_at
        self.category = category  # 'stock' or 'crypto'
        self.related_symbols = related_symbols or []
        self.image_url = image_url

    def __repr__(self):
        return f"<NewsArticle({self.category}): {self.headline[:50]}...>"


class NewsFetcher:
    """
    Fetches and categorizes financial news from Finnhub API.

    Finnhub provides real-time market news with excellent coverage
    of both stocks and cryptocurrency markets.
    """

    def __init__(self):
        """Initialize Finnhub news fetcher."""
        self.api_key = config.FINNHUB_API_KEY
        self.base_url = "https://finnhub.io/api/v1"

        if not self.api_key:
            logger.warning("Finnhub API key not configured!")

    def _categorize_news(self, headline: str, summary: str, category_hint: str = "") -> str:
        """
        Categorize news as 'stock', 'crypto', or 'general'.

        Args:
            headline: News headline
            summary: News summary/content
            category_hint: Optional category hint from API

        Returns:
            Category: 'stock', 'crypto', or 'general'
        """
        text = f"{headline} {summary} {category_hint}".lower()

        # Check for crypto keywords
        crypto_matches = sum(1 for keyword in config.CRYPTO_KEYWORDS if keyword in text)

        # Check for stock keywords
        stock_matches = sum(1 for keyword in config.STOCK_KEYWORDS if keyword in text)

        # Determine category based on keyword matches
        if crypto_matches > stock_matches and crypto_matches > 0:
            return 'crypto'
        elif stock_matches > crypto_matches and stock_matches > 0:
            return 'stock'
        elif crypto_matches > 0:
            return 'crypto'
        elif stock_matches > 0:
            return 'stock'
        else:
            return 'general'

    def fetch_general_news(self, category: str = 'general', limit: int = 10) -> List[NewsArticle]:
        """
        Fetch general financial news.

        Args:
            category: News category (general, forex, crypto, merger)
            limit: Maximum number of articles to fetch

        Returns:
            List of NewsArticle objects
        """
        try:
            url = f"{self.base_url}/news"
            params = {
                'category': category,
                'token': self.api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            articles = []
            for item in data[:limit]:
                # Determine category
                detected_category = self._categorize_news(
                    item.get('headline', ''),
                    item.get('summary', ''),
                    category
                )

                article = NewsArticle(
                    id=str(item.get('id', item.get('headline', ''))),
                    headline=item.get('headline', 'No headline'),
                    summary=item.get('summary', ''),
                    source=item.get('source', 'Unknown'),
                    url=item.get('url', ''),
                    published_at=datetime.fromtimestamp(item.get('datetime', 0)),
                    category=detected_category,
                    image_url=item.get('image', None)
                )
                articles.append(article)

            logger.info(f"Fetched {len(articles)} general news articles")
            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching general news: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching news: {e}", exc_info=True)
            return []

    def fetch_crypto_news(self, limit: int = 10) -> List[NewsArticle]:
        """
        Fetch cryptocurrency-specific news.

        Args:
            limit: Maximum number of articles to fetch

        Returns:
            List of NewsArticle objects
        """
        articles = self.fetch_general_news(category='crypto', limit=limit)

        # Ensure all are categorized as crypto
        for article in articles:
            if article.category != 'crypto':
                article.category = 'crypto'

        logger.info(f"Fetched {len(articles)} crypto news articles")
        return articles

    def fetch_company_news(self, symbol: str, limit: int = 5) -> List[NewsArticle]:
        """
        Fetch news for a specific company/stock.

        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            limit: Maximum number of articles to fetch

        Returns:
            List of NewsArticle objects
        """
        try:
            # Get date range (last 7 days)
            from datetime import date, timedelta
            to_date = date.today()
            from_date = to_date - timedelta(days=7)

            url = f"{self.base_url}/company-news"
            params = {
                'symbol': symbol,
                'from': from_date.isoformat(),
                'to': to_date.isoformat(),
                'token': self.api_key
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            articles = []
            for item in data[:limit]:
                article = NewsArticle(
                    id=str(item.get('id', item.get('headline', ''))),
                    headline=item.get('headline', 'No headline'),
                    summary=item.get('summary', ''),
                    source=item.get('source', 'Unknown'),
                    url=item.get('url', ''),
                    published_at=datetime.fromtimestamp(item.get('datetime', 0)),
                    category='stock',
                    related_symbols=[symbol],
                    image_url=item.get('image', None)
                )
                articles.append(article)

            logger.info(f"Fetched {len(articles)} news articles for {symbol}")
            return articles

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching company news for {symbol}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error fetching company news: {e}", exc_info=True)
            return []

    def fetch_all_news(self, general_limit: int = 10, crypto_limit: int = 10) -> List[NewsArticle]:
        """
        Fetch both general and crypto news.

        Args:
            general_limit: Max general news articles
            crypto_limit: Max crypto news articles

        Returns:
            Combined list of NewsArticle objects
        """
        all_articles = []

        # Fetch general/stock news
        general_news = self.fetch_general_news(category='general', limit=general_limit)
        all_articles.extend(general_news)

        # Fetch crypto news
        crypto_news = self.fetch_crypto_news(limit=crypto_limit)
        all_articles.extend(crypto_news)

        # Sort by published date (most recent first)
        all_articles.sort(key=lambda x: x.published_at, reverse=True)

        logger.info(
            f"Fetched {len(all_articles)} total articles "
            f"({sum(1 for a in all_articles if a.category == 'stock')} stock, "
            f"{sum(1 for a in all_articles if a.category == 'crypto')} crypto)"
        )

        return all_articles


if __name__ == '__main__':
    # Test the news fetcher
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("Testing Finnhub News Fetcher")
    print("=" * 60)

    fetcher = NewsFetcher()

    # Test general news
    print("\nFetching general news...")
    articles = fetcher.fetch_all_news(general_limit=5, crypto_limit=5)

    for article in articles[:10]:
        print(f"\n[{article.category.upper()}] {article.headline}")
        print(f"  Source: {article.source}")
        print(f"  Published: {article.published_at}")
        print(f"  URL: {article.url[:60]}...")
