#!/usr/bin/env python3
"""
Financial News Bot

Standalone bot that monitors financial news and sends updates to Telegram.
Runs continuously and fetches news from Finnhub API.

Usage:
    python main.py                  # Run with default interval (5 minutes)
    python main.py --interval 600   # Run with 10 minute interval
    python main.py --once           # Run once and exit (for testing)
"""

import logging
import argparse
import sys
from pathlib import Path

from app.engines.news_monitor.config import config
from app.engines.news_monitor.monitor import NewsMonitor


def setup_logging(log_level: str = "INFO"):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('news_monitor.log')
        ]
    )


def print_banner():
    """Print startup banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║              FINANCIAL NEWS MONITOR BOT                   ║
    ║                                                           ║
    ║  Real-time stock and crypto news delivered to Telegram   ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_config_info():
    """Print configuration information."""
    print("\n📋 Configuration:")
    print(f"  • Finnhub API: {'✅ Configured' if config.FINNHUB_API_KEY else '❌ Not configured'}")
    print(f"  • Telegram Bot: {'✅ Configured' if config.TELEGRAM_BOT_TOKEN else '❌ Not configured'}")
    print(f"  • Group Chat ID: {config.TELEGRAM_GROUP_CHAT_ID if config.TELEGRAM_GROUP_CHAT_ID else '❌ Not set'}")
    print(f"  • Stock News Topic: {config.STOCK_NEWS_TOPIC_ID if config.STOCK_NEWS_TOPIC_ID else '❌ Not set'}")
    print(f"  • Crypto News Topic: {config.CRYPTO_NEWS_TOPIC_ID if config.CRYPTO_NEWS_TOPIC_ID else '❌ Not set'}")
    print(f"  • Fetch Interval: {config.FETCH_INTERVAL}s ({config.FETCH_INTERVAL // 60} minutes)")
    print()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Financial News Monitor Bot',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Run continuously with 5 min interval
  python main.py --interval 600     # Run with 10 minute interval
  python main.py --once             # Run once for testing
  python main.py --log-level DEBUG  # Run with debug logging

Setup:
  1. Get Finnhub API key from https://finnhub.io/register
  2. Add FINNHUB_API_KEY to .env file
  3. Set STOCK_NEWS_TOPIC_ID and CRYPTO_NEWS_TOPIC_ID in .env
  4. Run this script
        """
    )

    parser.add_argument(
        '--interval',
        type=int,
        default=None,
        help='News fetch interval in seconds (default: from .env or 300)'
    )

    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (for testing)'
    )

    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (default: INFO)'
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    # Print banner
    print_banner()

    # Validate configuration
    try:
        config.validate()
        print("✅ Configuration validated successfully")
        print_config_info()
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}\n")
        print("Please check your .env file and ensure all required fields are set.")
        print("\nRequired configuration:")
        print("  • FINNHUB_API_KEY - Get from https://finnhub.io/register")
        print("  • BOT_TOKEN - Your Telegram bot token")
        print("  • GROUP_CHAT_ID - Your Telegram group chat ID")
        print("  • STOCK_NEWS_TOPIC_ID and/or CRYPTO_NEWS_TOPIC_ID - Topic IDs for news")
        print()
        sys.exit(1)

    # Create monitor
    logger.info("Initialising news monitor...")
    monitor = NewsMonitor()

    if args.once:
        # Run once for testing
        print("🔄 Running single news fetch cycle...")
        print("-" * 60)

        stats = monitor.run_once()

        print("\n📊 Results:")
        print(f"  • Total articles fetched: {stats.get('total', 0)}")
        print(f"  • New articles: {stats.get('new', 0)}")
        print(f"  • Duplicate articles (skipped): {stats.get('duplicate', 0)}")
        print(f"  • Stock news sent: {stats.get('stock_sent', 0)}")
        print(f"  • Crypto news sent: {stats.get('crypto_sent', 0)}")
        print(f"  • Failed: {stats.get('failed', 0)}")
        print("\n✅ Test complete")

    else:
        # Run continuously
        interval = args.interval or config.FETCH_INTERVAL

        print(f"🚀 Starting continuous monitoring...")
        print(f"   Fetch interval: {interval}s ({interval // 60} minutes)")
        print(f"   Press Ctrl+C to stop")
        print("-" * 60)
        print()

        try:
            monitor.run_forever(interval=interval)
        except KeyboardInterrupt:
            print("\n\n⏹️  News monitor stopped by user")
            logger.info("Shutdown complete")


if __name__ == '__main__':
    main()
