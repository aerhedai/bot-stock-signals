"""
Configuration module for the Telegram bot.
Loads environment variables and provides configuration settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from root .env file
_root_dir = Path(__file__).resolve().parent.parent
load_dotenv(_root_dir / '.env')

class Config:
    """Bot configuration class"""

    # Required: Telegram Bot Token
    BOT_TOKEN = os.getenv('BOT_TOKEN')

    # Optional: Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # Optional: Database URL
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///bot.db')

    # Optional: Admin user IDs
    ADMIN_IDS = [
        int(user_id.strip())
        for user_id in os.getenv('ADMIN_IDS', '').split(',')
        if user_id.strip()
    ]

    # Group chat ID for stock alerts
    GROUP_CHAT_ID = os.getenv('GROUP_CHAT_ID')

    # Optional: Default message thread/topic ID (for /testalert command)
    DEFAULT_MESSAGE_THREAD_ID = os.getenv('DEFAULT_MESSAGE_THREAD_ID')
    if DEFAULT_MESSAGE_THREAD_ID:
        DEFAULT_MESSAGE_THREAD_ID = int(DEFAULT_MESSAGE_THREAD_ID)

    # Stock Algorithm Configuration
    # P/E Ratio threshold (lower is better, default: 15)
    ALGO_PE_THRESHOLD = float(os.getenv('ALGO_PE_THRESHOLD', '15.0'))

    # PEG Ratio threshold (lower is better, default: 1.0)
    ALGO_PEG_THRESHOLD = float(os.getenv('ALGO_PEG_THRESHOLD', '1.0'))

    # Price-to-Book threshold (lower is better, default: 3.0)
    ALGO_PB_THRESHOLD = float(os.getenv('ALGO_PB_THRESHOLD', '3.0'))

    # Minimum market cap to consider (default: $1 billion)
    ALGO_MIN_MARKET_CAP = float(os.getenv('ALGO_MIN_MARKET_CAP', '1000000000'))

    # Minimum daily volume to consider (default: 100,000)
    ALGO_MIN_VOLUME = int(os.getenv('ALGO_MIN_VOLUME', '100000'))

    # Minimum score threshold for alerts (0-100, default: 60)
    ALGO_MIN_SCORE = float(os.getenv('ALGO_MIN_SCORE', '60.0'))

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.BOT_TOKEN:
            raise ValueError(
                "BOT_TOKEN is not set. Please create a .env file "
                "with your bot token from @BotFather"
            )
        return True
