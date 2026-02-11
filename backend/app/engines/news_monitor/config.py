"""
News Monitor Configuration

Loads configuration from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Get the root directory (5 levels up: config.py -> news_monitor/ -> engines/ -> app/ -> backend/ -> root)
_root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent

# Load environment variables from root .env
load_dotenv(_root_dir / '.env')


class NewsConfig:
    """News monitor configuration."""

    # Finnhub API
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')

    # Telegram Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    TELEGRAM_GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID', '')

    # Topic IDs for different news categories
    STOCK_NEWS_TOPIC_ID = int(os.getenv('STOCK_NEWS_TOPIC_ID', '0') or '0') or None
    CRYPTO_NEWS_TOPIC_ID = int(os.getenv('CRYPTO_NEWS_TOPIC_ID', '0') or '0') or None

    # News fetch interval (in seconds)
    FETCH_INTERVAL = int(os.getenv('NEWS_FETCH_INTERVAL', 300))  # 5 minutes default

    # News history database (stored locally in news_monitor/data/)
    MODULE_ROOT = Path(__file__).parent
    DATA_DIR = MODULE_ROOT / 'data'
    NEWS_HISTORY_FILE = DATA_DIR / 'news_history.json'

    # Crypto keywords for categorization
    CRYPTO_KEYWORDS = [
        'bitcoin', 'btc', 'ethereum', 'eth', 'crypto', 'cryptocurrency',
        'blockchain', 'defi', 'nft', 'altcoin', 'dogecoin', 'doge',
        'solana', 'sol', 'cardano', 'ada', 'ripple', 'xrp', 'binance',
        'bnb', 'polygon', 'matic', 'avalanche', 'avax', 'polkadot', 'dot',
        'chainlink', 'link', 'litecoin', 'ltc', 'stellar', 'xlm',
        'web3', 'metaverse', 'stablecoin', 'usdt', 'usdc', 'dai',
        'mining', 'miner', 'hash rate', 'wallet', 'exchange',
        'coinbase', 'kraken', 'ftx', 'crypto.com'
    ]

    # Stock keywords (to distinguish from general news)
    STOCK_KEYWORDS = [
        'stock', 'shares', 'equity', 'nasdaq', 'nyse', 's&p 500',
        'dow jones', 'market', 'earnings', 'revenue', 'profit',
        'dividend', 'ipo', 'merger', 'acquisition', 'trading',
        'analyst', 'upgrade', 'downgrade', 'bull', 'bear'
    ]

    @classmethod
    def validate(cls):
        """Validate configuration."""
        if not cls.FINNHUB_API_KEY:
            raise ValueError(
                "FINNHUB_API_KEY not set. Get your free API key from https://finnhub.io/"
            )

        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("BOT_TOKEN not set in .env file")

        if not cls.TELEGRAM_GROUP_CHAT_ID:
            raise ValueError("GROUP_CHAT_ID not set in .env file")

        if not cls.STOCK_NEWS_TOPIC_ID and not cls.CRYPTO_NEWS_TOPIC_ID:
            raise ValueError(
                "At least one of STOCK_NEWS_TOPIC_ID or CRYPTO_NEWS_TOPIC_ID must be set"
            )


# Create singleton instance
config = NewsConfig()
