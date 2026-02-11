# Crypto Sniper Bot

A sophisticated cryptocurrency **value investing** system that finds undervalued cryptos and alerts you when there's a valid entry signal. Uses a two-layer approach combining fundamental valuation with technical timing.

## Two-Layer Strategy

Unlike simple price alert bots, Crypto Sniper uses a **two-layer filtering system** similar to professional trading:

### Layer 1: VALUATION - Is it Undervalued?
Identifies cryptocurrencies trading below their fair value using multiple valuation methods.

### Layer 2: TECHNICAL TRIGGER - Is it Time to Enter?
Waits for confirmation signals before alerting (RSI oversold, Bollinger bounce, MACD crossover, etc.).

**⚠️ IMPORTANT**: Alerts are ONLY sent when BOTH layers confirm. This ensures you're buying undervalued assets at the right time.

---

## Valuation Methods (Layer 1)

The bot uses **4 independent valuation strategies** to find undervalued cryptocurrencies:

### 1. Historical Z-Score Valuation
**What it does**: Compares current price to 6-month historical average

**When it triggers**: Price is 1.5+ standard deviations below average

**What it means**: Crypto is significantly cheaper than its recent historical norm

**Example**: If ETH typically trades at $3,000 ±$500, and it's now at $2,200, the Z-score would be around -1.6 (undervalued)

```
Z-Score = (Current Price - Mean Price) / Std Deviation
Threshold: ≤ -1.5
```

### 2. Volume-Weighted Fair Value
**What it does**: Calculates volume-weighted average price (VWAP) over 90 days

**When it triggers**: Current price is 10%+ below VWAP

**What it means**: Price is below what most traders paid recently (they're underwater)

**Example**: If the 90-day VWAP is $50 and current price is $44, that's a 12% discount

```
VWAP = Σ(Price × Volume) / Σ(Volume)
Threshold: ≥ 10% discount
```

### 3. Relative Underperformance vs Bitcoin
**What it does**: Compares 90-day performance against Bitcoin

**When it triggers**: Crypto has underperformed BTC by 15%+

**What it means**: While BTC rose, this crypto lagged significantly (potential catch-up trade)

**Example**: If BTC is up 20% over 90 days, but SOL is only up 3%, SOL has underperformed by 17%

```
Relative Performance = Crypto Return - BTC Return
Threshold: ≤ -15%
```

### 4. Bollinger Band Mean Reversion
**What it does**: Identifies when price breaks below 50-day Bollinger lower band

**When it triggers**: Price is 10%+ below lower Bollinger Band

**What it means**: Extreme oversold condition, likely to revert to mean

**Example**: If lower BB is at $100 and price is at $88, that's a 12% deviation (strong reversion signal)

```
Lower BB = SMA(50) - (2 × Std Dev)
Threshold: ≥ 10% below lower band
```

---

## Technical Triggers (Layer 2)

Once a crypto passes valuation, the bot waits for one of these **entry triggers**:

### 1. RSI Oversold
- **RSI ≤ 30** (deeply oversold)
- Indicates selling exhaustion, potential bounce

### 2. Bollinger Bounce
- **Price drops below lower BB** then starts recovering
- Classic mean reversion setup

### 3. MACD Bullish Crossover
- **MACD crosses above signal line**
- Momentum shifting from bearish to bullish

### 4. Low Volatility Consolidation
- **Volatility < 3%** over 10 days
- Compression often precedes expansion (breakout)

### 5. Golden Cross ⭐
- **50-MA crosses above 200-MA**
- Most powerful bullish signal

---

## How It Works (Example)

Let's say SOL (Solana) is being analyzed:

```
Step 1: VALUATION CHECK
├─ Historical Z-Score: -1.8 ✅ (Trading 1.8 std devs below 6-mo average)
├─ Volume Fair Value: 8% discount ❌ (Below 10% threshold)
├─ Relative to BTC: -18% underperformance ✅ (Lagged BTC significantly)
└─ Bollinger: 12% below lower band ✅ (Extreme oversold)

Result: 3/4 methods show undervalued → PASS Layer 1
Best method: Bollinger Mean Reversion (score: 75/100)

Step 2: TECHNICAL TRIGGER CHECK
├─ RSI: 28 ✅ (Oversold, potential bounce)
├─ MACD: Still bearish ❌
└─ BB Position: Below lower band ✅ (Mean reversion setup)

Result: RSI Oversold trigger detected → PASS Layer 2

✅ BOTH LAYERS PASSED → SEND ALERT!

Combined Score: 68/100 (Valuation 60% + Technical 40%)
Severity: MEDIUM
```

**Alert Message**:
```
📊 Solana (SOL-USD) - MEDIUM

💰 Price: $98.50

📈 VALUATION
Method: Bollinger Mean Reversion
Score: 75/100
Fair Value: $115.20
Discount: 14.5% undervalued

🎯 ENTRY TRIGGER
Signal: RSI oversold at 28.0
RSI: 28.0 (Oversold)
MACD: Bearish ❌
BB: Below lower (oversold)

📊 PERFORMANCE
1 Day: 🔴 -2.3%
7 Days: 🔴 -8.5%
30 Days: 🔴 -15.2%

Score: 68/100
Category: Major
Confidence: High
```

---

## Features

✅ **Value-First Approach**: Only alerts on undervalued cryptos (not random pumps)

✅ **Technical Confirmation**: Waits for proper entry timing

✅ **4 Valuation Methods**: Multiple perspectives on fair value

✅ **5 Technical Triggers**: RSI, Bollinger, MACD, Volatility, Golden Cross

✅ **Scoring System**: 0-100 combined score (Valuation 60% + Technical 40%)

✅ **Severity Levels**: Critical (85+), High (70+), Medium (50+), Low (<50)

✅ **Smart Cooldowns**: Won't spam same crypto (60min cooldown)

✅ **25+ Cryptos Monitored**: BTC, ETH, SOL, ADA, LINK, AVAX, and more

---

## Installation

```bash
# 1. Navigate to crypto_sniper
cd crypto_sniper

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
nano .env  # Add your Telegram tokens

# 4. Test (single scan)
python main.py --once

# 5. Run continuously
python main.py
```

---

## Configuration

### Valuation Thresholds (Layer 1)

Edit `.env` to adjust how strict the valuation filters are:

```bash
# Historical Z-Score
ZSCORE_THRESHOLD=-1.5              # More negative = stricter (-2.0 = very strict)
ZSCORE_LOOKBACK_DAYS=180           # History period (90-365 days)

# Volume Fair Value
VOLUME_FV_DISCOUNT_THRESHOLD=0.10  # Min discount vs VWAP (0.05-0.20)
VOLUME_FV_PERIOD=90                # VWAP period (30-180 days)

# Relative vs BTC
BTC_UNDERPERFORMANCE_THRESHOLD=-15.0  # Underperformance % (-10 to -25)
BTC_COMPARISON_DAYS=90             # Comparison period (30-180 days)

# Bollinger Mean Reversion
BB_MEAN_REVERSION_MIN_DEVIATION=0.10  # Distance below BB (0.05-0.20)
BB_MEAN_REVERSION_PERIOD=50       # BB period (20-100 days)
```

### Technical Triggers (Layer 2)

```bash
# RSI Settings
RSI_PERIOD=14                      # Standard RSI period
RSI_OVERSOLD=30                    # Oversold threshold (20-35)

# Bollinger Bands
BB_PERIOD=20                       # Standard is 20
BB_STD_DEV=2                       # Standard is 2

# MACD (hardcoded as 12/26/9)
```

### Scanning & Alerts

```bash
# How often to scan (recommend 30-60 min for daily analysis)
SCAN_INTERVAL_MINUTES=30

# Cooldown between alerts for same crypto
ALERT_COOLDOWN_MINUTES=60
```

---

## Cryptocurrency Watchlist

Monitors 25+ cryptocurrencies across multiple categories:

**Major (10)**: BTC, ETH, BNB, XRP, ADA, DOGE, SOL, DOT, MATIC, LTC

**DeFi (7)**: UNI, LINK, AVAX, ATOM, AAVE, CRV, MKR

**Altcoins (8)**: SHIB, APT, ARB, OP, INJ, SUI, SEI, TIA

Edit `crypto_sniper/config/crypto_list.py` to customize.

---

## Understanding Signals

### Severity Levels

- **🚨 CRITICAL** (85-100): Extremely undervalued + strong technical trigger
- **⚠️ HIGH** (70-84): Significantly undervalued + good entry point
- **📊 MEDIUM** (50-69): Moderately undervalued + valid trigger
- **ℹ️ LOW** (0-49): Mild undervaluation + weak trigger

### Combined Score Formula

```
Combined Score = (Valuation Score × 60%) + (Technical Score × 40%)

Valuation Score: 0-100 based on discount %
Technical Score: Critical=100, High=80, Medium=60, Low=40
```

### Confidence Levels

- **High**: 180+ days of data, strong valuation signal
- **Medium**: 100-179 days of data, moderate signal
- **Low**: < 100 days of data, weak signal

---

## Performance Tips

### For More Signals (Aggressive)
```bash
ZSCORE_THRESHOLD=-1.0              # Less strict
VOLUME_FV_DISCOUNT_THRESHOLD=0.05  # Lower discount needed
BTC_UNDERPERFORMANCE_THRESHOLD=-10.0
RSI_OVERSOLD=35                    # Looser trigger
```

### For Higher Quality (Conservative)
```bash
ZSCORE_THRESHOLD=-2.0              # Very strict
VOLUME_FV_DISCOUNT_THRESHOLD=0.15  # Higher discount needed
BTC_UNDERPERFORMANCE_THRESHOLD=-20.0
RSI_OVERSOLD=25                    # Tighter trigger
```

### For Day Trading (Faster Signals)
```bash
SCAN_INTERVAL_MINUTES=15
ZSCORE_LOOKBACK_DAYS=90            # Shorter history
ALERT_COOLDOWN_MINUTES=30
```

### For Swing Trading (Patient)
```bash
SCAN_INTERVAL_MINUTES=60
ZSCORE_LOOKBACK_DAYS=365           # Longer history
ALERT_COOLDOWN_MINUTES=240         # 4 hours
```

---

## File Structure

```
crypto_sniper/
├── main.py                  # Entry point with scheduler
├── requirements.txt         # Dependencies
├── .env                     # Your configuration
├── .env.example             # Configuration template
│
├── config/
│   ├── settings.py          # All settings and thresholds
│   └── crypto_list.py       # Crypto watchlist
│
├── core/
│   ├── valuation.py         # 🆕 4 valuation methods (Layer 1)
│   ├── indicators.py        # Technical indicators
│   └── monitor.py           # 🆕 Two-layer scanning logic
│
├── interface/
│   └── telegram_bot.py      # 🆕 Enhanced message formatting
│
├── data/
│   └── alerts.json          # Alert history
│
└── logs/
    └── crypto_sniper.log    # Application logs
```

---

## Advanced Usage

### Programmatic Access

```python
from crypto_sniper import CryptoMonitor, CRYPTO_WATCHLIST

# Initialize
monitor = CryptoMonitor()

# Analyze single crypto
signal = monitor.analyze_crypto('BTC-USD')

if signal:
    print(f"✅ {signal.name}")
    print(f"   Valuation: {signal.valuation_method} ({signal.valuation_score}/100)")
    print(f"   Trigger: {signal.trigger_description}")
    print(f"   Discount: {signal.discount_percentage:.1f}%")
    print(f"   Score: {signal.combined_score}/100")
else:
    print("❌ No signal (not undervalued or no trigger)")

# Scan all
signals = monitor.scan_multiple(CRYPTO_WATCHLIST)
print(f"Found {len(signals)} opportunities")
```

### Custom Valuation Method

Add to `crypto_sniper/core/valuation.py`:

```python
def method_5_custom(self, symbol: str, price_data: pd.DataFrame) -> Optional[ValuationResult]:
    """Your custom valuation logic."""
    # Your calculation here

    return ValuationResult(
        method_name="Custom Method",
        is_undervalued=True,
        score=75,
        current_price=current_price,
        fair_value_estimate=fair_value,
        discount_percentage=discount
    )
```

---

## Troubleshooting

### "No signals found"

**Possible reasons**:
1. **Market is overvalued** - No cryptos are undervalued right now
2. **Thresholds too strict** - Lower ZSCORE_THRESHOLD or VOLUME_FV_DISCOUNT_THRESHOLD
3. **No technical triggers** - Cryptos are undervalued but no entry signal yet (be patient!)

### "Too many signals"

**Solutions**:
1. **Increase thresholds** - Make valuation criteria stricter
2. **Require multiple methods** - Modify code to require 2+ valuation methods
3. **Higher severity only** - Filter for HIGH/CRITICAL in main.py

### "Signals not actionable"

**Tips**:
- Focus on HIGH and CRITICAL severity only
- Look for combined_score ≥ 75
- Prefer signals with "High" confidence
- Wait for multiple consecutive confirmations

---

## Comparison: Before vs After

### Before (Simple Price Tracker)
❌ Alerts on ANY price movement (pumps and dumps)
❌ No concept of fair value
❌ Reactive to noise
❌ High false positive rate

### After (Value Investor)
✅ Only alerts on undervalued cryptos
✅ 4 independent valuation methods
✅ Waits for confirmation
✅ High signal quality

---

## License

Same as parent project.

---

## Quick Start Summary

```bash
# Install
cd crypto_sniper
pip install -r requirements.txt

# Configure
cp .env.example .env
nano .env  # Add tokens

# Test
python main.py --once

# Run
python main.py
```

**Expected behavior**: Bot will scan every 30 minutes. Most scans will find **0-2 signals** (this is normal - we're looking for rare value opportunities, not constant noise).
