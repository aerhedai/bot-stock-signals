# Stock Sniper Bot - Quick Start Guide

Get the bot running in **5 minutes**!

---

## Important: Working Directory

**Run all commands from the parent directory** (`/Users/rohan/bot-telegram-signals/`), not from inside `stock_sniper/`:

```bash
# You should be here:
cd /Users/rohan/bot-telegram-signals

# NOT here:
# cd /Users/rohan/bot-telegram-signals/stock_sniper  ❌
```

---

## Step 1: Install Dependencies (2 minutes)

```bash
pip install -r stock_sniper/requirements.txt
```

---

## Step 2: Configure Telegram (2 minutes)

### Get Your Bot Token

1. Open Telegram and message [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow instructions
3. Copy your bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Get Your Chat ID

1. Add your bot to your Telegram group
2. In your **existing** bot (the one already running), send `/getadminids` in the group
3. Copy the Chat ID from the response

### Configure Environment

```bash
# Copy example config (if you haven't already)
cp stock_sniper/.env.example stock_sniper/.env

# Edit .env file
nano stock_sniper/.env
```

Set these two values:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
TELEGRAM_CHAT_ID=your_chat_id_from_getadminids
```

Save and exit (Ctrl+X, Y, Enter)

**Note**: Your `.env` file should be at `stock_sniper/.env`

---

## Step 3: Test the Bot (1 minute)

```bash
# Run a single test scan (either command works)
python stock_sniper/main.py --once

# Or as a module:
python -m stock_sniper.main --once
```

You should see:
- ✅ Configuration loaded
- ✅ Scanning 150 tickers (takes ~2 minutes)
- ✅ Statistics displayed
- ✅ Likely 1-3 signals detected and sent to Telegram!

---

## Step 4: Start Production Mode

```bash
# Run with scheduler (scans every hour)
python stock_sniper/main.py
```

You should receive a Telegram message:
```
ℹ️ Status Update

Stock Sniper Bot started successfully!

📊 Monitoring 50 stocks
⏰ Scanning every 60 minutes
🛡️ Alert cooldown: 7 days

First scan will run at next scheduled interval.
```

**Done!** The bot is now running. Leave it running in the background.

---

## Optional: Run in Background

### Using screen (recommended)

```bash
# Start a screen session
screen -S sniper

# Run the bot
python stock_sniper/main.py

# Detach: Press Ctrl+A, then D
# Reattach later: screen -r sniper
```

### Using nohup

```bash
nohup python stock_sniper/main.py > sniper_output.log 2>&1 &
```

### Using systemd (Linux)

Create `/etc/systemd/system/stock-sniper.service`:

```ini
[Unit]
Description=Stock Sniper Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/bot-telegram-signals
ExecStart=/usr/bin/python3 stock_sniper/main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable stock-sniper
sudo systemctl start stock-sniper
sudo systemctl status stock-sniper
```

---

## Monitoring

### View Live Logs

```bash
tail -f stock_sniper/logs/sniper.log
```

### Check Alert History

```bash
cat stock_sniper/data/alerts.json
```

### View Statistics

Check logs for the "📊 Statistics" section after each scan.

---

## What to Expect

### First 24 Hours

- **Scans**: 24 (one per hour)
- **Signals**: 5-20 (depends on market conditions)
- **Alerts**: 0-2 (most signals will be throttled)

### First Week

- **Scans**: 168
- **Signals**: 50-150
- **Alerts**: 5-10 (builds up alert history)

### Steady State

- **Alerts**: 1-2 per day on average
- **Quality**: High (multiple confirmations required)

---

## Troubleshooting

### "No signals detected"

**Possible reasons:**
- Market is bearish (SPY < 200-SMA) → Wait for bullish regime
- No stocks currently undervalued → Normal, be patient
- Stocks undervalued but below EMA → Waiting for trigger

**Check**: Look at logs for specific reasons per ticker

### "Telegram error"

**Check:**
1. Bot token is correct
2. Chat ID is correct (negative number for groups)
3. Bot is a member of the group
4. Bot has permission to post messages

**Test**: Run `python stock_sniper/interface/telegram_bot.py` to test connection

### "API rate limiting"

**Solution:**
- Reduce scan frequency in `.env`: `SCAN_INTERVAL_MINUTES=120`
- Or implement caching (see PERFORMANCE_REPORT.md)

---

## Next Steps

1. **Monitor for 1 week** - Observe signal patterns
2. **Read README.md** - Understand how strategies work
3. **Review PERFORMANCE_REPORT.md** - Optimization recommendations
4. **Adjust settings** - Fine-tune thresholds in `.env`

---

## Getting Alerts

When a valid signal is detected, you'll receive a Telegram message like:

```
🎯 SNIPER ALERT: UNDERVALUED STOCK DETECTED
==================================================

📊 Ticker: AAPL
⏰ Time: 2026-01-08 14:30:00

💰 VALUATION METHOD: Z-Score
   • Score: 78.5/100
   • Current Price: $145.23
   • Target Price: $158.40 (+9.1%)

📈 TECHNICAL TRIGGER: ✅ TRIGGERED
🛡️ SAFETY CHECKS: ✅ All passed
```

**Important**: This is a screening tool, not financial advice. Always do your own research before trading!

---

## Support

- **Documentation**: See README.md for detailed info
- **Performance**: See PERFORMANCE_REPORT.md for optimization
- **Issues**: Check logs first, then debug with `--once` mode

---

**Happy Sniping! 🎯**
