# Financial News Monitor

Automated system that monitors real-time financial news for stocks and cryptocurrencies and sends updates to separate Telegram topics.

## Features

- **Real-time News**: Fetches latest financial news from Finnhub API (60 requests/minute free tier)
- **Smart Categorisation**: Automatically categorises news as stock or crypto using keyword analysis
- **Separate Topics**: Sends stock news and crypto news to different Telegram topics/threads
- **Duplicate Prevention**: Tracks sent articles to avoid sending duplicates
- **Configurable Intervals**: Set custom fetch intervals (default: 5 minutes)
- **Rich Formatting**: Beautifully formatted messages with emojis and HTML styling
- **Automatic Cleanup**: Old news history auto-cleaned after 7 days

## Setup

### 1. Get Finnhub API Key

1. Go to [https://finnhub.io/register](https://finnhub.io/register)
2. Sign up for a free account
3. Copy your API key from the dashboard

### 2. Configure Telegram Topics

You need to create two topics in your Telegram group (one for stocks, one for crypto):

1. Open your Telegram group
2. Enable "Topics" (Group Settings → Topics → Enable)
3. Create two topics:
   - "Stock News" (for stock-related news)
   - "Crypto News" (for cryptocurrency news)

### 3. Get Topic IDs

Send a message in each topic, then visit:
```
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```

Look for `message_thread_id` in the response for each topic.

### 4. Update .env File

Add the following to your `.env` file:

```bash
# Finnhub API Key
FINNHUB_API_KEY=your_finnhub_api_key_here

# Stock News Topic ID
STOCK_NEWS_TOPIC_ID=5

# Crypto News Topic ID
CRYPTO_NEWS_TOPIC_ID=6

# News fetch interval (seconds) - default: 300 (5 minutes)
NEWS_FETCH_INTERVAL=300
```

### 5. Install Dependencies

```bash
cd news_monitor
pip install -r requirements.txt
```

## Usage

### Run Continuously (Production)

```bash
cd news_monitor
python main.py
```

This will:
- Fetch news every 5 minutes (or custom interval)
- Send stock news to the stock topic
- Send crypto news to the crypto topic
- Run continuously until stopped with Ctrl+C

### Test Mode (Run Once)

```bash
cd news_monitor
python main.py --once
```

This will fetch and send news once, then exit. Great for testing configuration.

### Custom Interval

```bash
cd news_monitor

# Fetch news every 10 minutes
python main.py --interval 600

# Fetch news every 30 minutes
python main.py --interval 1800
```

### Debug Mode

```bash
cd news_monitor
python main.py --log-level DEBUG
```

## How It Works

### News Fetching

The system fetches news from Finnhub API in two categories:
1. **General Financial News**: Latest market news
2. **Crypto-Specific News**: Cryptocurrency and blockchain news

### Categorisation Logic

Each article is analysed using keyword matching:

**Crypto Keywords**: bitcoin, ethereum, crypto, blockchain, defi, nft, etc.
**Stock Keywords**: stock, shares, nasdaq, earnings, dividend, ipo, etc.

The system counts keyword matches and categorises accordingly.

### Message Format

Each news article is formatted as:

```
📈 Headline Goes Here

Brief summary of the article (if available, max 300 chars)...

🕐 2 hours ago • 📡 Bloomberg
🏷 AAPL, MSFT
🔗 Read more
```

### Duplicate Prevention

The system maintains a history database (`data/news_history.json`) that tracks:
- Article IDs
- Send timestamps
- Categories
- Headlines

Articles are never sent twice. History is automatically cleaned after 7 days.

## File Structure

```
news_monitor/
├── __init__.py          # Module initialisation
├── config.py            # Configuration management
├── fetcher.py           # Finnhub API integration
├── formatter.py         # Telegram message formatting
├── history.py           # Duplicate tracking
├── monitor.py           # Main monitoring service
├── main.py              # Standalone launcher script
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables (create from .env.example)
├── .env.example         # Environment variable template
├── README.md            # This file
└── data/                # Data directory (auto-created)
    └── news_history.json # Sent articles database (auto-created)
```

## API Rate Limits

**Finnhub Free Tier**:
- 60 API calls per minute
- 30 API calls per second
- No daily limit (but be respectful!)

**Recommended Intervals**:
- **5 minutes (300s)**: 12 fetches/hour, ~288 fetches/day ✅
- **10 minutes (600s)**: 6 fetches/hour, ~144 fetches/day ✅
- **1 minute (60s)**: 60 fetches/hour, ~1440 fetches/day (approaching limits)

## Troubleshooting

### No news being sent

1. Check API key: `echo $FINNHUB_API_KEY`
2. Verify topic IDs in .env
3. Run with `--once` flag to test
4. Check logs in `news_bot.log`

### "Configuration Error"

Make sure all required fields are set in `.env`:
- `FINNHUB_API_KEY`
- `BOT_TOKEN`
- `GROUP_CHAT_ID`
- At least one of: `STOCK_NEWS_TOPIC_ID` or `CRYPTO_NEWS_TOPIC_ID`

### Too many duplicates being skipped

This is normal! News APIs often return the same articles multiple times. The duplicate detection is working correctly.

### Rate limit errors

Increase your fetch interval:
```bash
python news_bot.py --interval 600  # 10 minutes
```

## Advanced Usage

### Running as Background Service

#### Linux/Mac (using screen):
```bash
screen -S news_monitor
cd news_monitor
python main.py
# Press Ctrl+A, then D to detach
```

To reattach: `screen -r news_monitor`

#### Linux (systemd service):

Create `/etc/systemd/system/news-monitor.service`:
```ini
[Unit]
Description=Financial News Monitor Bot
After=network.target

[Service]
Type=simple
User=your_user
WorkingDirectory=/path/to/bot-telegram-signals/news_monitor
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl enable news-monitor
sudo systemctl start news-monitor
sudo systemctl status news-monitor
```

### Custom Categorisation

Edit `news_monitor/config.py` to modify keyword lists:
- `CRYPTO_KEYWORDS`: Add/remove crypto-related terms
- `STOCK_KEYWORDS`: Add/remove stock-related terms

### Integration with Other Bots

You can import and use the NewsMonitor in other Python scripts:

```python
from news_monitor import NewsMonitor

monitor = NewsMonitor()

# Run once
stats = monitor.run_once()
print(f"Sent {stats['stock_sent']} stock news, {stats['crypto_sent']} crypto news")

# Or run continuously
monitor.run_forever(interval=300)
```

## Support

For issues or questions:
1. Check `news_monitor.log` for errors
2. Run with `--log-level DEBUG` for verbose output
3. Test with `--once` flag first

## Quick Setup Summary

```bash
# 1. Navigate to news_monitor directory
cd news_monitor

# 2. Copy and configure environment file
cp .env.example .env
# Edit .env with your API keys and settings

# 3. Install dependencies
pip install -r requirements.txt

# 4. Test the setup
python main.py --once

# 5. Run continuously
python main.py
```

## License

Same as parent project.
