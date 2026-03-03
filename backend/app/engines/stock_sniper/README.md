# Stock Sniper Bot 🎯

A sophisticated, production-ready algorithmic trading bot that identifies undervalued stock opportunities and sends real-time alerts via Telegram.

## Overview

The Stock Sniper Bot combines **fundamental analysis**, **statistical methods**, and **technical triggers** to detect high-probability undervalued stocks. It runs on a schedule, scanning a diversified watchlist of 50 stocks and alerting you when all conditions align.

### Key Features

- **3 Valuation Strategies**: Graham Number (deep value), Z-Score (panic reversion), Linear Regression (trend deviation)
- **Safety Mechanisms**: Market regime detection, earnings trap avoidance
- **Technical Confirmation**: EMA-based trigger to confirm momentum
- **Smart Throttling**: 7-day cooldown per ticker to prevent alert spam
- **Telegram Integration**: Formatted alerts sent directly to your chat/channel
- **Modular Architecture**: Clean, maintainable, extensible codebase

---

## Architecture

```
/stock_sniper
  ├── /config          # Configuration and settings
  │     ├── settings.py    (All parameters, thresholds, env loading)
  │     └── tickers.py     (50-stock watchlist across sectors)
  │
  ├── /core            # Core business logic
  │     ├── safety.py      (Market regime + earnings checks)
  │     ├── strategies.py  (3 valuation methods with scoring)
  │     └── scanner.py     (EMA trigger + signal orchestration)
  │
  ├── /interface       # External communication
  │     └── telegram_bot.py (Message formatting, sending, throttling)
  │
  ├── /data            # Persistent storage
  │     └── alerts.json    (Alert history for throttling)
  │
  ├── /logs            # Application logs
  │     └── sniper.log
  │
  ├── main.py          # Entry point with scheduler
  ├── requirements.txt # Python dependencies
  └── .env             # Environment configuration
```

---

## How It Works

### The 3-Stage Pipeline

Every stock goes through this pipeline on each scan:

#### Stage 1: Safety Checks 🛡️

**Market Regime Check**
- Compares SPY to its 200-day SMA
- Blocks all signals if market is bearish (SPY < 200-SMA)
- Prevents buying into a falling market

**Earnings Trap Check**
- Checks if earnings announcement is within 3 days
- Blocks signals for stocks near earnings
- Avoids volatility and surprises

#### Stage 2: Valuation Strategies 💰

Three independent methods evaluate undervaluation:

**Method 1: Graham Number (Deep Value)**
```
Graham Price = √(22.5 × EPS × Book Value Per Share)
Trigger: Current Price < 80% of Graham Price
```
- Identifies stocks trading below intrinsic value
- Based on Benjamin Graham's value investing principles
- Best for: Fundamentally sound, profitable companies

**Method 2: Z-Score (Panic Reversion)**
```
Z-Score = (Current Price - 20-day Mean) / Std Deviation
Trigger: Z-Score < -2.0
```
- Detects statistically oversold conditions
- Looks for mean reversion opportunities
- Best for: Temporary panic sells, volatility spikes

**Method 3: Linear Regression (Trend Deviation)**
```
Fit 6-month trend line using sklearn
Trigger: Positive slope AND price > 10% below trend
```
- Identifies dips in uptrending stocks
- Combines momentum with value
- Best for: Growth stocks having temporary pullbacks

**Scoring System**
- Each method returns a 0-100 confidence score
- Higher scores = stronger conviction
- Bot uses the highest-scoring method per stock

#### Stage 3: Technical Trigger 📈

**EMA Confirmation**
- Calculates 20-period Exponential Moving Average
- Only triggers when price closes above EMA
- Uses closed candles only (no repainting)
- Confirms momentum is turning bullish

**Final Signal**
Only if ALL conditions are met:
1. ✅ Market regime healthy
2. ✅ No earnings within 3 days
3. ✅ At least one valuation method triggered
4. ✅ Price above EMA-20

---

## Installation

### 1. Install Dependencies

```bash
cd stock_sniper
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example configuration
cp .env.example .env

# Edit .env with your values
nano .env
```

Required variables:
- `TELEGRAM_BOT_TOKEN`: From @BotFather
- `TELEGRAM_CHAT_ID`: Your group/channel ID (use /getadminids)

### 3. Verify Setup

Test individual components:

```bash
# Test safety checks
python stock_sniper/core/safety.py

# Test valuation strategies
python stock_sniper/core/strategies.py

# Test scanner
python stock_sniper/core/scanner.py

# Test Telegram interface
python stock_sniper/interface/telegram_bot.py
```

---

## Usage

### Run with Scheduler (Production)

```bash
python stock_sniper/main.py
```

- Scans every 60 minutes (configurable)
- Sends startup notification
- Logs all activity to `logs/sniper.log`
- Press Ctrl+C to stop gracefully

### Run Single Scan (Testing)

```bash
python stock_sniper/main.py --once
```

- Runs one complete scan immediately
- Useful for testing configuration changes
- Shows detailed output

### Monitor Logs

```bash
# Follow live logs
tail -f stock_sniper/logs/sniper.log

# View recent activity
tail -100 stock_sniper/logs/sniper.log
```

---

## Configuration

All settings are in `config/settings.py` and can be overridden via `.env`:

### Safety Settings

```env
MARKET_CHECK_ENABLED=true           # Enable SPY regime check
EARNINGS_CHECK_ENABLED=true         # Enable earnings trap check
SPY_SMA_PERIOD=200                  # Market SMA period
EARNINGS_BUFFER_DAYS=3              # Days before earnings to avoid
```

### Strategy Thresholds

```env
# Graham Number
GRAHAM_DISCOUNT_THRESHOLD=0.80      # Buy below 80% of Graham price

# Z-Score
ZSCORE_PERIOD=20                    # Days for mean/std calculation
ZSCORE_THRESHOLD=-2.0               # Oversold threshold

# Linear Regression
REGRESSION_LOOKBACK_MONTHS=6        # Months of data for trend
REGRESSION_DEVIATION_THRESHOLD=0.10 # 10% below trend line
```

### Technical Trigger

```env
EMA_PERIOD=20                       # EMA period
EMA_TIMEFRAME=1d                    # 1d (daily) or 4h
REQUIRE_PRICE_ABOVE_EMA=true        # Must be above EMA
USE_CLOSED_CANDLES_ONLY=true        # Prevent repainting
```

### Alert Throttling

```env
ALERT_COOLDOWN_DAYS=7               # Days between alerts per ticker
SCAN_INTERVAL_MINUTES=60            # Minutes between scans
```

---

## Watchlist

The bot monitors **50 diversified stocks** across sectors:

- **Technology** (12): AAPL, MSFT, GOOGL, META, NVDA, AMD, INTC, CRM, ADBE, ORCL, CSCO, IBM
- **Finance** (8): JPM, BAC, WFC, C, GS, MS, V, MA
- **Healthcare** (8): JNJ, UNH, PFE, ABBV, MRK, LLY, TMO, ABT
- **Consumer** (8): AMZN, TSLA, WMT, HD, NKE, MCD, SBUX, TGT
- **Energy/Industrials** (7): XOM, CVX, BA, CAT, GE, DE, UPS
- **Staples/Materials** (7): PG, KO, PEP, PM, CL, COST, FCX

**Customise**: Edit `config/tickers.py` to add/remove stocks.

---

## Alert Format

Telegram alerts include:

```
🎯 SNIPER ALERT: UNDERVALUED STOCK DETECTED
==================================================

📊 Ticker: AAPL
⏰ Time: 2026-01-08 14:30:00

💰 VALUATION METHOD: Z-Score
   • Score: 78.5/100
   • Z-Score: -2.35 (OVERSOLD, threshold: -2.0, -8.2% from mean)
   • Current Price: $145.23
   • Target Price: $158.40 (+9.1%)

📈 TECHNICAL TRIGGER:
   • Price $145.23 ABOVE EMA(20) $142.15 (+2.2%)
   • Status: ✅ TRIGGERED

🛡️ SAFETY CHECKS:
   • Market Regime: ✅ Healthy
     (SPY $475.30 vs 200-SMA $468.50)
   • Earnings: ✅ Safe
     (Next earnings in 28 days)

==================================================
⚠️ This is algorithmic analysis. Do your own research.
```

---

## Alert History & Throttling

The bot tracks all sent alerts in `data/alerts.json`:

```json
{
  "alerts": {
    "AAPL": [
      {
        "timestamp": "2026-01-08T14:30:00",
        "method": "Z-Score",
        "score": 78.5,
        "price": 145.23,
        "target": 158.40
      }
    ]
  },
  "last_updated": "2026-01-08T14:30:05"
}
```

**7-Day Cooldown**: After sending an alert for a ticker, the bot won't alert on that ticker again for 7 days (configurable). This prevents spam while allowing re-entry after sufficient time.

---

## Performance Metrics

The bot logs statistics after each scan:

```
📊 Statistics:
  Total scans: 24
  Total signals found: 8
  Total alerts sent: 5
  Last scan duration: 12.3s
  Bot uptime: 24.0 hours
```

**Typical Performance**:
- Scan duration: 10-15 seconds (50 stocks)
- Signals per day: 1-5 (depending on market conditions)
- Alerts sent: 0-2 per day (after throttling)

---

## Troubleshooting

### No Signals Generated

**Possible causes**:
1. Market regime bearish (SPY < 200-SMA)
2. No stocks meet valuation thresholds
3. Stocks undervalued but below EMA (waiting for trigger)
4. Recent earnings announcements blocking signals

**Solution**: Check logs for specific reasons. Run with verbose mode:
```python
# In main.py, change:
signals = self.scanner.scan_multiple(
    tickers=self.watchlist,
    verbose=True,  # Enable detailed logging
    stop_on_signal=False
)
```

### Telegram Alerts Not Sending

**Check**:
1. `TELEGRAM_BOT_TOKEN` is correct
2. `TELEGRAM_CHAT_ID` is correct (use /getadminids)
3. Bot has permissions in the group
4. Internet connection is stable

**Test manually**:
```bash
python stock_sniper/interface/telegram_bot.py
```

### High API Rate Limiting

yfinance has rate limits. If scanning fails:
1. Reduce scan frequency (`SCAN_INTERVAL_MINUTES`)
2. Reduce watchlist size
3. Add delays between API calls

---

## Advanced Usage

### Custom Watchlist

Edit `config/tickers.py`:

```python
# Add your own tickers
CUSTOM_WATCHLIST = ['NVDA', 'TSLA', 'PLTR', 'COIN']

# Or use sector-specific lists
from config.tickers import TECHNOLOGY, HEALTHCARE
MY_WATCHLIST = TECHNOLOGY + HEALTHCARE
```

### Adjust Strategy Sensitivity

Make strategies more/less aggressive in `.env`:

**More Aggressive** (more signals):
```env
GRAHAM_DISCOUNT_THRESHOLD=0.85      # Accept smaller discount
ZSCORE_THRESHOLD=-1.5               # Lower oversold threshold
REGRESSION_DEVIATION_THRESHOLD=0.05 # Only 5% below trend
REQUIRE_PRICE_ABOVE_EMA=false       # Don't require EMA confirmation
```

**More Conservative** (fewer, higher quality signals):
```env
GRAHAM_DISCOUNT_THRESHOLD=0.70      # Require 30% discount
ZSCORE_THRESHOLD=-2.5               # Extreme oversold only
REGRESSION_DEVIATION_THRESHOLD=0.15 # 15% below trend
REGRESSION_MIN_R_SQUARED=0.7        # Strong trend only
```

### Integration with Existing Bot

The Stock Sniper can run alongside your existing Telegram bot:

```python
# In your bot.py
from stock_sniper.core import get_scanner
from stock_sniper.interface import get_telegram_bot

# Add slash command
async def scan_now(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Trigger manual scan."""
    scanner = get_scanner()
    signals = scanner.scan_multiple(WATCHLIST, verbose=False)

    if signals:
        bot = get_telegram_bot()
        for signal in signals:
            bot.send_signal(signal)
        await update.message.reply_text(f"✅ Found {len(signals)} signal(s)!")
    else:
        await update.message.reply_text("No signals detected.")
```

---

## Testing

### Unit Tests

Test individual components:

```bash
# Test each module
python -m stock_sniper.core.safety
python -m stock_sniper.core.strategies
python -m stock_sniper.core.scanner
python -m stock_sniper.interface.telegram_bot
```

### Integration Test

Run a complete scan on a single ticker:

```python
from stock_sniper.core import get_scanner

scanner = get_scanner()
signal = scanner.scan_single('AAPL', verbose=True)

if signal:
    print(scanner.format_signal(signal))
else:
    print("No signal generated")
```

---

## Logging

Logs are written to both console and `logs/sniper.log`:

```
2026-01-08 14:30:00 - root - INFO - ============================================================
2026-01-08 14:30:00 - root - INFO - Starting scheduled scan #1
2026-01-08 14:30:00 - root - INFO - ============================================================
2026-01-08 14:30:02 - root - INFO - Market Regime: SPY=$475.30, 200-SMA=$468.50, Status=✓ HEALTHY
2026-01-08 14:30:12 - root - INFO - ✓ SIGNAL: AAPL via Z-Score (Score: 78.5)
2026-01-08 14:30:13 - root - INFO - AAPL: Alert sent successfully to Telegram
```

**Log Levels** (set in `.env`):
- `DEBUG`: Verbose output for debugging
- `INFO`: Standard operation logs (recommended)
- `WARNING`: Only warnings and errors
- `ERROR`: Only errors

---

## Best Practices

### 1. Start Conservative

Begin with default settings and observe results for 1-2 weeks before adjusting.

### 2. Monitor Logs Daily

Check logs for patterns:
- Are signals being generated but throttled?
- Are scans completing successfully?
- Any recurring errors?

### 3. Backtest Strategy Changes

Before modifying thresholds, test on historical data to see impact.

### 4. Diversify Watchlist

Include stocks across sectors to avoid concentration risk.

### 5. Don't Override Blindly

The bot is a screening tool, not trading advice. Always verify:
- Company fundamentals
- Recent news
- Overall market conditions

### 6. Use Throttling

Keep `ALERT_COOLDOWN_DAYS` at 5-7 to avoid alert fatigue.

### 7. Regular Maintenance

- Update watchlist quarterly
- Review alert history monthly
- Update yfinance regularly (`pip install --upgrade yfinance`)

---

## Roadmap

Potential future enhancements:

- [ ] Backtesting framework with historical data
- [ ] Additional valuation methods (DCF, DDM)
- [ ] Sector rotation strategies
- [ ] Portfolio position sizing recommendations
- [ ] Web dashboard for monitoring
- [ ] Integration with broker APIs for auto-trading
- [ ] Machine learning for strategy optimisation
- [ ] Multi-timeframe analysis
- [ ] Options strategy suggestions
- [ ] Risk management rules

---

## FAQ

**Q: How often should I run scans?**
A: 60 minutes is recommended. More frequent scans won't improve results (prices don't change that fast) and may hit API limits.

**Q: Can I run this 24/7?**
A: Yes, but US market hours (9:30 AM - 4:00 PM ET) are most relevant. Consider scheduling around those times.

**Q: What if I get too many alerts?**
A: Increase `ALERT_COOLDOWN_DAYS` or make strategies more conservative.

**Q: What if I get no alerts?**
A: Check if market regime is bearish. Try reducing thresholds slightly or disabling `REQUIRE_PRICE_ABOVE_EMA`.

**Q: Is this financial advice?**
A: No. This is a screening tool for educational purposes. Always do your own research.

**Q: Can I use this for day trading?**
A: The strategies are designed for swing/position trading (days to weeks), not day trading.

**Q: What about cryptocurrencies?**
A: yfinance supports some crypto. Add BTC-USD, ETH-USD, etc. to watchlist, but strategies may need adjustment.

---

## Support

For issues, questions, or contributions:

1. Check logs for error messages
2. Verify configuration in `.env`
3. Test individual modules
4. Review this documentation

---

## License

This project is for educational and personal use. Not financial advice. Use at your own risk.

---

## Acknowledgments

Built with:
- [yfinance](https://github.com/ranaroussi/yfinance) - Market data
- [scikit-learn](https://scikit-learn.org/) - ML algorithms
- [pandas](https://pandas.pydata.org/) - Data processing
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram integration

Inspired by:
- Benjamin Graham's value investing principles
- Statistical arbitrage and mean reversion strategies
- Technical analysis best practices

---

**Happy Sniping! 🎯📈**
