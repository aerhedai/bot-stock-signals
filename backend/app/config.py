"""
Unified configuration for the backend application.
Uses Pydantic Settings to load all env vars from root .env.
"""

from pydantic_settings import BaseSettings
from pydantic import Field, field_validator
from pathlib import Path
from typing import Optional


def _empty_to_none(v):
    """Convert empty strings to None for optional int fields."""
    if v == "" or v is None:
        return None
    return v


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Telegram
    bot_token: str = Field("", alias="BOT_TOKEN")
    group_chat_id: str = Field("", alias="GROUP_CHAT_ID")
    admin_ids: str = Field("", alias="ADMIN_IDS")
    default_message_thread_id: Optional[int] = Field(None, alias="DEFAULT_MESSAGE_THREAD_ID")

    # Stock Sniper Telegram (separate tokens for engine bots)
    telegram_bot_token: str = Field("", alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field("", alias="TELEGRAM_CHAT_ID")
    telegram_thread_id: Optional[str] = Field(None, alias="TELEGRAM_THREAD_ID")

    # News Monitor
    finnhub_api_key: str = Field("", alias="FINNHUB_API_KEY")
    stock_news_topic_id: Optional[int] = Field(None, alias="STOCK_NEWS_TOPIC_ID")
    crypto_news_topic_id: Optional[int] = Field(None, alias="CRYPTO_NEWS_TOPIC_ID")
    news_fetch_interval: int = Field(300, alias="NEWS_FETCH_INTERVAL")

    @field_validator("stock_news_topic_id", "crypto_news_topic_id", "default_message_thread_id", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        return _empty_to_none(v)

    # General
    log_level: str = Field("INFO", alias="LOG_LEVEL")
    database_url: str = Field("sqlite:///bot.db", alias="DATABASE_URL")

    # Stock algorithm thresholds
    algo_pe_threshold: float = Field(15.0, alias="ALGO_PE_THRESHOLD")
    algo_peg_threshold: float = Field(1.0, alias="ALGO_PEG_THRESHOLD")
    algo_pb_threshold: float = Field(3.0, alias="ALGO_PB_THRESHOLD")
    algo_min_market_cap: float = Field(1_000_000_000, alias="ALGO_MIN_MARKET_CAP")
    algo_min_volume: int = Field(100_000, alias="ALGO_MIN_VOLUME")
    algo_min_score: float = Field(60.0, alias="ALGO_MIN_SCORE")

    # Scan intervals (minutes)
    stock_scan_interval: int = 60
    crypto_scan_interval: int = 30
    news_scan_interval: int = 5

    model_config = {
        "env_file": str(Path(__file__).resolve().parent.parent.parent / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
