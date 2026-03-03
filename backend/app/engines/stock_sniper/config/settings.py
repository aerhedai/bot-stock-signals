"""
Configuration Settings for Stock Sniper Bot

This module contains all configurable parameters for the bot including
thresholds, timeframes, and environment variable loading.
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Get the base directory (stock_sniper/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from root .env
load_dotenv(BASE_DIR.parent.parent.parent.parent / '.env')

# =============================================================================
# TELEGRAM CONFIGURATION
# =============================================================================
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')
TELEGRAM_THREAD_ID = os.getenv('STOCK_SNIPER_TOPIC_ID', None)  # Topic ID for stock alerts

# =============================================================================
# SAFETY THRESHOLDS
# =============================================================================

# Market Regime Settings
SPY_SMA_PERIOD = 200  # 200-day Simple Moving Average for SPY
MARKET_CHECK_ENABLED = True  # Set to False to disable market regime check

# Earnings Trap Settings
EARNINGS_BUFFER_DAYS = 3  # Avoid stocks with earnings within X days
EARNINGS_CHECK_ENABLED = True  # Set to False to disable earnings check

# =============================================================================
# STRATEGY THRESHOLDS
# =============================================================================

# Method 1: Graham Number (Deep Value)
GRAHAM_DISCOUNT_THRESHOLD = 0.80  # Current price must be < 80% of Graham Price
GRAHAM_MIN_EPS = 0.01  # Minimum EPS to avoid negative/zero values
GRAHAM_MIN_BOOK_VALUE = 0.01  # Minimum book value per share

# Method 2: Z-Score (Panic Reversion)
ZSCORE_PERIOD = 20  # Days for calculating mean and std dev
ZSCORE_THRESHOLD = -2.0  # Standard deviations below mean (e.g., -2.0)
ZSCORE_MIN_DATA_POINTS = 25  # Minimum data points needed for calculation

# Method 3: Linear Regression (Trend Deviation)
REGRESSION_LOOKBACK_MONTHS = 6  # Months of historical data
REGRESSION_DEVIATION_THRESHOLD = 0.10  # 10% below trend line
REGRESSION_MIN_SLOPE = 0.0001  # Minimum positive slope to confirm uptrend
REGRESSION_MIN_R_SQUARED = 0.3  # Minimum R² for reliable trend

# =============================================================================
# TECHNICAL TRIGGER SETTINGS
# =============================================================================

# EMA Trigger Configuration
EMA_PERIOD = 20  # 20-period Exponential Moving Average
EMA_TIMEFRAME = '1d'  # '1d' for daily, '4h' for 4-hour
EMA_MIN_DATA_POINTS = 30  # Minimum candles needed

# Trigger Confirmation
REQUIRE_PRICE_ABOVE_EMA = True  # Must close above EMA to trigger
USE_CLOSED_CANDLES_ONLY = True  # Use only completed candles (prevent repainting)

# =============================================================================
# ALERT THROTTLING
# =============================================================================

ALERT_COOLDOWN_DAYS = 7  # Days before re-alerting same ticker
ALERT_HISTORY_FILE = str(BASE_DIR / 'data' / 'alerts.json')

# =============================================================================
# SCANNING CONFIGURATION
# =============================================================================

SCAN_INTERVAL_MINUTES = 60  # Run scan every X minutes
MAX_CONCURRENT_REQUESTS = 5  # Limit API calls
REQUEST_DELAY_SECONDS = 0.5  # Delay between API requests

# Data Fetching
DATA_CACHE_DURATION_MINUTES = 30  # Cache duration for price data
MAX_RETRIES = 3  # Retry failed API calls
RETRY_DELAY_SECONDS = 2  # Delay between retries

# =============================================================================
# LOGGING CONFIGURATION
# =============================================================================

LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = str(BASE_DIR / 'logs' / 'sniper.log')
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# =============================================================================
# PERFORMANCE TRACKING
# =============================================================================

ENABLE_PERFORMANCE_LOGGING = True  # Track scan performance metrics
PERFORMANCE_LOG_FILE = str(BASE_DIR / 'data' / 'performance.json')

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

    if GRAHAM_DISCOUNT_THRESHOLD <= 0 or GRAHAM_DISCOUNT_THRESHOLD >= 1:
        errors.append("GRAHAM_DISCOUNT_THRESHOLD must be between 0 and 1")

    if ZSCORE_THRESHOLD >= 0:
        errors.append("ZSCORE_THRESHOLD should be negative (e.g., -2.0)")

    if REGRESSION_DEVIATION_THRESHOLD <= 0 or REGRESSION_DEVIATION_THRESHOLD >= 1:
        errors.append("REGRESSION_DEVIATION_THRESHOLD must be between 0 and 1")

    if EMA_PERIOD < 5:
        errors.append("EMA_PERIOD too low, minimum recommended is 5")

    if ALERT_COOLDOWN_DAYS < 1:
        errors.append("ALERT_COOLDOWN_DAYS must be at least 1")

    if errors:
        raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))

    return True

# Validate on import
try:
    validate_config()
except ValueError as e:
    print(f"⚠️  Configuration Warning: {e}")
    print("Please check your settings.py and .env file")
