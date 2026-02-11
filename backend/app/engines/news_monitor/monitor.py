"""
News Monitor Service

Main service that fetches news, filters duplicates, and sends to Telegram topics.
Runs on a scheduled interval.
"""

import logging
import requests
import time
from typing import List, Dict
from datetime import datetime

from app.engines.news_monitor.config import config
from app.engines.news_monitor.fetcher import NewsFetcher, NewsArticle
from app.engines.news_monitor.formatter import NewsFormatter
from app.engines.news_monitor.history import NewsHistory

logger = logging.getLogger(__name__)


class NewsMonitor:
    """
    Main news monitoring service.

    Fetches news from Finnhub, categorizes, and sends to appropriate Telegram topics.
    """

    def __init__(self):
        """Initialize news monitor."""
        self.fetcher = NewsFetcher()
        self.formatter = NewsFormatter()
        self.history = NewsHistory(str(config.NEWS_HISTORY_FILE))

        self.bot_token = config.TELEGRAM_BOT_TOKEN
        self.chat_id = config.TELEGRAM_GROUP_CHAT_ID
        self.stock_topic_id = config.STOCK_NEWS_TOPIC_ID
        self.crypto_topic_id = config.CRYPTO_NEWS_TOPIC_ID

        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"

        logger.info("News Monitor initialized")

    def send_telegram_message(self, text: str, topic_id: int = None) -> bool:
        """
        Send a message to Telegram.

        Args:
            text: Message text (HTML formatted)
            topic_id: Topic/thread ID to send to

        Returns:
            True if successful, False otherwise
        """
        try:
            url = f"{self.base_url}/sendMessage"

            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': 'HTML',
                'disable_web_page_preview': False
            }

            # Add thread ID if specified
            if topic_id:
                payload['message_thread_id'] = topic_id

            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            result = response.json()

            if result.get('ok'):
                logger.debug(f"Message sent to topic {topic_id}")
                return True
            else:
                logger.error(f"Telegram API error: {result}")
                return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending message: {e}", exc_info=True)
            return False

    def process_articles(self, articles: List[NewsArticle]) -> Dict[str, int]:
        """
        Process and send news articles.

        Args:
            articles: List of NewsArticle objects

        Returns:
            Statistics dictionary
        """
        stats = {
            'total': len(articles),
            'new': 0,
            'duplicate': 0,
            'stock_sent': 0,
            'crypto_sent': 0,
            'failed': 0
        }

        for article in articles:
            # Check if already sent
            if self.history.is_sent(article.id):
                stats['duplicate'] += 1
                logger.debug(f"Skipping duplicate: {article.headline[:50]}")
                continue

            stats['new'] += 1

            # Format message
            message = self.formatter.format_article(article, include_summary=True)

            # Determine topic based on category
            topic_id = None
            if article.category == 'stock' and self.stock_topic_id:
                topic_id = self.stock_topic_id
            elif article.category == 'crypto' and self.crypto_topic_id:
                topic_id = self.crypto_topic_id
            else:
                logger.debug(f"No topic configured for {article.category} news")
                continue

            # Send to Telegram
            success = self.send_telegram_message(message, topic_id)

            if success:
                # Mark as sent
                self.history.mark_sent(
                    news_id=article.id,
                    category=article.category,
                    headline=article.headline,
                    url=article.url
                )

                if article.category == 'stock':
                    stats['stock_sent'] += 1
                elif article.category == 'crypto':
                    stats['crypto_sent'] += 1

                # Small delay to avoid rate limiting
                time.sleep(0.5)
            else:
                stats['failed'] += 1

        return stats

    def fetch_and_send(self, general_limit: int = 10, crypto_limit: int = 10) -> Dict[str, int]:
        """
        Main method: fetch news and send to Telegram.

        Args:
            general_limit: Max general news articles to fetch
            crypto_limit: Max crypto news articles to fetch

        Returns:
            Statistics dictionary
        """
        logger.info("Starting news fetch cycle...")

        try:
            # Fetch news
            articles = self.fetcher.fetch_all_news(
                general_limit=general_limit,
                crypto_limit=crypto_limit
            )

            if not articles:
                logger.warning("No articles fetched")
                return {'total': 0, 'new': 0}

            # Process and send
            stats = self.process_articles(articles)

            logger.info(
                f"News cycle complete: {stats['new']} new, {stats['duplicate']} duplicate, "
                f"{stats['stock_sent']} stock sent, {stats['crypto_sent']} crypto sent, "
                f"{stats['failed']} failed"
            )

            return stats

        except Exception as e:
            logger.error(f"Error in fetch_and_send: {e}", exc_info=True)
            return {'total': 0, 'new': 0, 'error': str(e)}

    def run_once(self) -> Dict[str, int]:
        """Run one cycle of news monitoring."""
        return self.fetch_and_send()

    def run_forever(self, interval: int = None):
        """
        Run news monitoring continuously.

        Args:
            interval: Fetch interval in seconds (default from config)
        """
        if interval is None:
            interval = config.FETCH_INTERVAL

        logger.info(f"Starting continuous news monitoring (interval: {interval}s)")

        # Send startup message
        startup_msg = self.formatter.format_status(
            f"News Monitor started\n"
            f"Fetch interval: {interval}s ({interval // 60} minutes)\n"
            f"Stock topic: {'✅' if self.stock_topic_id else '❌'}\n"
            f"Crypto topic: {'✅' if self.crypto_topic_id else '❌'}"
        )

        if self.stock_topic_id:
            self.send_telegram_message(startup_msg, self.stock_topic_id)
        if self.crypto_topic_id:
            self.send_telegram_message(startup_msg, self.crypto_topic_id)

        cycle = 0

        try:
            while True:
                cycle += 1
                logger.info(f"=== News Cycle #{cycle} ===")

                # Run fetch cycle
                stats = self.run_once()

                # Log stats
                logger.info(f"Cycle #{cycle} stats: {stats}")

                # Wait for next cycle
                logger.info(f"Sleeping for {interval}s until next cycle...")
                time.sleep(interval)

        except KeyboardInterrupt:
            logger.info("News monitor stopped by user")

            # Send shutdown message
            shutdown_msg = self.formatter.format_status(
                f"News Monitor stopped\n"
                f"Total cycles: {cycle}\n"
                f"History stats: {self.history.get_stats()}"
            )

            if self.stock_topic_id:
                self.send_telegram_message(shutdown_msg, self.stock_topic_id)
            if self.crypto_topic_id:
                self.send_telegram_message(shutdown_msg, self.crypto_topic_id)

        except Exception as e:
            logger.error(f"Fatal error in monitor loop: {e}", exc_info=True)

            # Send error message
            error_msg = self.formatter.format_error(f"Fatal error: {str(e)}")

            if self.stock_topic_id:
                self.send_telegram_message(error_msg, self.stock_topic_id)
            if self.crypto_topic_id:
                self.send_telegram_message(error_msg, self.crypto_topic_id)


if __name__ == '__main__':
    # Test the news monitor
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    print("Testing News Monitor")
    print("=" * 60)

    # Validate config
    try:
        config.validate()
        print("✓ Configuration valid")
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        exit(1)

    # Create monitor
    monitor = NewsMonitor()

    # Run once
    print("\nRunning single fetch cycle...")
    stats = monitor.run_once()
    print(f"\nStats: {stats}")

    print("\n" + "=" * 60)
    print("Test complete. To run continuously, use: monitor.run_forever()")
