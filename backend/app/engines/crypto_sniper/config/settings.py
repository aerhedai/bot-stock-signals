"""
Configuration Settings for Crypto Sniper Bot

This module contains all configurable parameters for the crypto monitoring bot.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Get the base directory (crypto_sniper/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from root .env
load_dotenv(BASE_DIR.parent.parent.parent.parent / '.env')

# =============================================================================
# TELEGRAM CONFIGURATION
# =============================================================================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
TELEGRAM_THREAD_ID = os.getenv('CRYPTO_SNIPER_TOPIC_ID', None)  # Topic ID for crypto alerts

# =============================================================================
# MONITORING SETTINGS
# =============================================================================

# Scan interval (how often to check prices)
SCAN_INTERVAL_MINUTES = int(os.getenv('SCAN_INTERVAL_MINUTES', 5))

# Price change thresholds (percentage)
PRICE_CHANGE_THRESHOLD_1H = float(os.getenv('PRICE_CHANGE_THRESHOLD_1H', 3.0))
PRICE_CHANGE_THRESHOLD_24H = float(os.getenv('PRICE_CHANGE_THRESHOLD_24H', 10.0))
PRICE_CHANGE_THRESHOLD_7D = float(os.getenv('PRICE_CHANGE_THRESHOLD_7D', 20.0))

# Volume spike threshold
VOLUME_SPIKE_THRESHOLD = float(os.getenv('VOLUME_SPIKE_THRESHOLD', 200.0))

# Minimum market cap to monitor
MIN_MARKET_CAP = float(os.getenv('MIN_MARKET_CAP', 1000000000))

# =============================================================================
# TECHNICAL INDICATORS
# =============================================================================

# RSI Settings
RSI_PERIOD = int(os.getenv('RSI_PERIOD', 14))
RSI_OVERBOUGHT = int(os.getenv('RSI_OVERBOUGHT', 70))
RSI_OVERSOLD = int(os.getenv('RSI_OVERSOLD', 30))

# Moving Average Settings
MA_SHORT_PERIOD = int(os.getenv('MA_SHORT_PERIOD', 9))
MA_LONG_PERIOD = int(os.getenv('MA_LONG_PERIOD', 21))

# Bollinger Bands Settings
BB_PERIOD = int(os.getenv('BB_PERIOD', 20))
BB_STD_DEV = int(os.getenv('BB_STD_DEV', 2))

# =============================================================================
# ALERT SETTINGS
# =============================================================================

# Cooldown between alerts for same crypto (minutes)
ALERT_COOLDOWN_MINUTES = int(os.getenv('ALERT_COOLDOWN_MINUTES', 60))
ALERT_HISTORY_FILE = str(BASE_DIR / 'data' / 'alerts.json')

# =============================================================================
# DATA SETTINGS
# =============================================================================

# Price data cache duration
CACHE_DURATION_MINUTES = 5

# Historical data periods
LOOKBACK_1H = '1h'
LOOKBACK_24H = '1d'
LOOKBACK_7D = '7d'
LOOKBACK_30D = '30d'

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = str(BASE_DIR / 'logs' / 'crypto_sniper.log')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# =============================================================================
# VALIDATION
# =============================================================================

def validate_config():
    """Validate critical configuration settings."""
    errors = []

    if not TELEGRAM_BOT_TOKEN:
        errors.append("TELEGRAM_BOT_TOKEN not set in environment variables")

    if not TELEGRAM_CHAT_ID:
        errors.append("TELEGRAM_CHAT_ID not set in environment variables")

    if SCAN_INTERVAL_MINUTES < 1:
        errors.append("SCAN_INTERVAL_MINUTES must be at least 1")

    if PRICE_CHANGE_THRESHOLD_1H <= 0:
        errors.append("PRICE_CHANGE_THRESHOLD_1H must be positive")

    if ALERT_COOLDOWN_MINUTES < 0:
        errors.append("ALERT_COOLDOWN_MINUTES must be non-negative")

    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

    return True


# Validate on import
try:
    validate_config()
except ValueError as e:
    print(f"⚠️  Configuration Warning: {e}")
    print("Please check your settings.py and .env file")
