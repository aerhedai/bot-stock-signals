# Telegram Signals Bot

A fullstack financial signals platform. Scans stocks and crypto for undervalued opportunities using algorithmic strategies, monitors market news, delivers alerts to Telegram, and surfaces everything through a real-time dashboard — with an AI agent layer powered by Gemini 2.5 Flash.

---

## Contents

- [Architecture](#architecture)
- [Services](#services)
- [Backend](#backend)
  - [Engines](#engines)
  - [AI Agent](#ai-agent)
  - [API Reference](#api-reference)
  - [Scheduler](#scheduler)
  - [Configuration](#configuration)
- [Frontend](#frontend)
- [Telegram Bot](#telegram-bot)
- [Running the Project](#running-the-project)
- [Development Setup](#development-setup)
- [Data Storage](#data-storage)

---

## Architecture

```
bot-telegram-signals/
├── backend/                  # FastAPI backend + analysis engines
│   ├── app/
│   │   ├── main.py           # FastAPI app factory, lifespan management
│   │   ├── config.py         # Pydantic Settings — all env vars
│   │   ├── dependencies.py   # Singleton providers (scheduler, alert store)
│   │   ├── api/v1/           # REST endpoints
│   │   │   ├── health.py
│   │   │   ├── stocks.py
│   │   │   ├── crypto.py
│   │   │   ├── news.py
│   │   │   ├── analysis.py
│   │   │   ├── dashboard.py
│   │   │   └── router.py
│   │   ├── models/           # Pydantic response schemas
│   │   ├── services/
│   │   │   ├── scheduler.py        # APScheduler job management
│   │   │   ├── alert_store.py      # JSON read/write for all data files
│   │   │   ├── ai_service.py       # Gemini Vertex AI client
│   │   │   └── agent_orchestrator.py # Central AI agent with tool registry
│   │   └── engines/
│   │       ├── stock_sniper/       # Stock valuation scanner
│   │       ├── crypto_sniper/      # Crypto technical monitor
│   │       ├── news_monitor/       # Finnhub news fetcher
│   │       ├── market_analysis/    # AI market summary generator
│   │       └── dashboard/          # Dashboard aggregation orchestrator
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/                 # Next.js 16 dashboard (TypeScript + Tailwind v4)
│   ├── src/
│   │   ├── app/              # Pages: dashboard, predictions, analysis, news, settings
│   │   ├── components/       # UI components
│   │   ├── lib/              # api.ts, types.ts, format.ts
│   │   └── hooks/            # useApi data-fetching hook
│   └── Dockerfile
│
├── telegram/                 # Standalone Telegram bot
│   ├── bot.py
│   ├── handlers/
│   └── Dockerfile
│
├── docker-compose.yml
└── .env                      # All secrets and configuration (not tracked)
```

---

## Services

Three containers, one `docker-compose.yml`:

| Service | Port | Description |
|---|---|---|
| `backend` | `8000` | FastAPI — REST API, signal engines, scheduler, AI agent |
| `frontend` | `3000` | Next.js dashboard |
| `telegram-bot` | — | Telegram bot (connects to Telegram API, no exposed port) |

The frontend and telegram-bot depend on the backend being healthy before starting.

---

## Backend

**Stack:** Python 3.14 · FastAPI · APScheduler · Pydantic v2 · uv

**Key dependencies:** `yfinance`, `pandas`, `numpy`, `scikit-learn`, `google-genai`, `python-telegram-bot`, `apscheduler`

### Engines

#### Stock Sniper

Scans a watchlist of stocks against three valuation strategies. Signals are stored per-ticker and sent to a Telegram topic.

**Strategies:**

| Strategy | Method | Time Horizon | Condition |
|---|---|---|---|
| Graham Number | `√(22.5 × EPS × Book Value)` | Long-Term (3–12 months) | Price < 80% of Graham price |
| Z-Score Reversion | Statistical deviation from mean | Short-Term (1–5 days) | Z-score ≤ −2 (panic oversell) |
| Linear Regression | Trend line deviation | Swing Trade (1–4 weeks) | Price significantly below regression trend |

**Safety checks run before any signal fires:**
- **Market regime** — SPY must be above its 200-day SMA (bull market filter)
- **Earnings trap** — skips tickers with earnings within 3 days

**Signal scoring:** 0–100 confidence score. Minimum score to fire: `60.0` (configurable).

**Scan interval:** every 60 minutes.

---

#### Crypto Sniper

Monitors a crypto watchlist for technical entry signals using price action and indicators.

**Triggers:**
- RSI ≤ 30 (oversold)
- Bollinger Band lower breach
- 24h / 7d price change thresholds
- Volume spikes

**Scan interval:** every 30 minutes.

---

#### News Monitor

Fetches financial news from Finnhub on two tracks:

1. **General news** — `GET /news?category=general` and `GET /news?category=crypto`. Categorised by keyword matching and sent to Telegram stock/crypto topics.
2. **Ticker news** — `GET /company-news?symbol={ticker}` for each recently-active signal ticker. Stored with ticker association for per-stock news panels. **Not sent to Telegram** — used for dashboard enrichment and the AI agent.

**Retention:** 14 days. **General fetch interval:** every 5 minutes. **Ticker fetch interval:** every 60 minutes.

---

#### Market Analysis

AI-generated market summaries using recent news headlines. The agent reads the headline pool and cached analysis, decides if a refresh is needed (>3 hours old or significantly more headlines available), and writes a new 5–7 sentence summary if so.

**Runs:** every 24 hours, and on-demand via `POST /api/v1/analysis/trigger`.

---

#### Dashboard Orchestrator

Drives the `/api/v1/dashboard` endpoint. On each request, an AI agent:
1. Reads recent stock and crypto signals
2. Reads market headlines for both categories
3. Reads existing analysis summaries
4. Decides whether to refresh stale analysis
5. Returns a 2–3 sentence market picture alongside fully-structured data

---

### AI Agent

**Model:** `gemini-2.5-flash` via Google Vertex AI

**Architecture:** Central `AgentOrchestrator` singleton with a tool registry. Features register their tools at startup; the agent can invoke any registered tool during a multi-turn session.

**Rate limit:** 20 agent calls per hour (system-wide, configurable in `agent_orchestrator.py`).

**Registered tools:**

| Tool | Registered by | Description |
|---|---|---|
| `get_market_headlines` | MarketAnalyzer | Recent news headlines by category (stock/crypto) |
| `get_market_analysis` | MarketAnalyzer | Current cached analysis for a category |
| `update_market_analysis` | MarketAnalyzer | Write a new analysis to cache |
| `get_ticker_headlines` | MarketAnalyzer | Last 14 days of headlines for a specific ticker |
| `get_stock_signals` | DashboardOrchestrator | Recent stock sniper alerts |
| `get_crypto_signals` | DashboardOrchestrator | Recent crypto sniper alerts |

---

### API Reference

All endpoints are documented interactively at `http://localhost:8000/docs`.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/health/status` | Scheduler stats for all services |
| GET | `/api/v1/stocks/signals` | Latest stock signal per ticker |
| GET | `/api/v1/stocks/watchlist` | Watchlist grouped by sector |
| GET | `/api/v1/stocks/chart/{ticker}` | 90-day OHLCV + EMA20 for chart |
| GET | `/api/v1/stocks/ai-insight/{ticker}` | On-demand AI insight for a ticker |
| POST | `/api/v1/stocks/scan` | Trigger immediate stock scan |
| GET | `/api/v1/crypto/signals` | Latest crypto signal per symbol |
| GET | `/api/v1/crypto/watchlist` | Crypto watchlist by category |
| GET | `/api/v1/crypto/chart/{symbol}` | Price + Bollinger Bands + RSI |
| GET | `/api/v1/crypto/ai-insight/{symbol}` | On-demand AI insight for a symbol |
| POST | `/api/v1/crypto/scan` | Trigger immediate crypto scan |
| GET | `/api/v1/news/feed` | All recent news articles |
| GET | `/api/v1/news/ticker/{ticker}` | Last 14 days of news for a ticker (fetches live from Finnhub on cache miss) |
| POST | `/api/v1/news/fetch` | Trigger immediate news fetch |
| GET | `/api/v1/analysis/stocks` | Cached stock market analysis |
| GET | `/api/v1/analysis/crypto` | Cached crypto market analysis |
| POST | `/api/v1/analysis/trigger` | Trigger AI analysis refresh |
| GET | `/api/v1/dashboard` | Full dashboard payload (AI-orchestrated) |

---

### Scheduler

Five recurring jobs managed by APScheduler:

| Job | Interval | What it does |
|---|---|---|
| `stock_scan` | 60 min | Scans full stock watchlist, upserts signals |
| `crypto_scan` | 30 min | Scans crypto watchlist, upserts signals |
| `news_fetch` | 5 min | Fetches general + crypto news, sends to Telegram |
| `ticker_news_fetch` | 60 min | Fetches company news for recently active signal tickers |
| `market_analysis` | 24 hours | AI analysis refresh pass |

---

### Configuration

All configuration is loaded from the root `.env` file via Pydantic Settings.

```env
# Telegram
BOT_TOKEN=                        # Main bot token (dashboard bot)
GROUP_CHAT_ID=                    # Telegram group ID for alerts
TELEGRAM_BOT_TOKEN=               # Token used by stock/crypto sniper engines
TELEGRAM_CHAT_ID=                 # Chat ID used by sniper engines
STOCK_NEWS_TOPIC_ID=              # Telegram topic for stock news
CRYPTO_NEWS_TOPIC_ID=             # Telegram topic for crypto news
STOCK_SNIPER_TOPIC_ID=            # Telegram topic for stock signals
CRYPTO_SNIPER_TOPIC_ID=           # Telegram topic for crypto signals

# APIs
FINNHUB_API_KEY=                  # finnhub.io — news fetching

# Google Vertex AI (AI agent)
VERTEX_PROJECT=                   # GCP project ID
VERTEX_LOCATION=us-central1       # Region (default: us-central1)
VERTEX_MODEL=gemini-2.5-flash     # Model ID (default: gemini-2.5-flash)
GOOGLE_APPLICATION_CREDENTIALS=   # Path to service account JSON

# Stock algorithm thresholds (optional overrides)
ALGO_PE_THRESHOLD=15.0
ALGO_PEG_THRESHOLD=1.0
ALGO_PB_THRESHOLD=3.0
ALGO_MIN_MARKET_CAP=1000000000    # $1B minimum market cap
ALGO_MIN_VOLUME=100000
ALGO_MIN_SCORE=60.0               # Minimum signal confidence score (0–100)

# Intervals
NEWS_FETCH_INTERVAL=300           # Seconds (default 5 min)
```

---

## Frontend

**Stack:** Next.js 16 · React 19 · TypeScript · Tailwind CSS v4 · Recharts

**Pages:**

| Route | Description |
|---|---|
| `/` | Dashboard — AI briefing, recent signals, news highlights, market analysis |
| `/predictions/stocks` | Stock signals — expandable cards with Chart and News tabs, sort controls |
| `/predictions/crypto` | Crypto signals — same expandable card pattern |
| `/analysis` | AI market analysis for stocks and crypto |
| `/news` | News feed — category tabs (All/Stock/Crypto), search, company ticker badges |
| `/settings` | App settings |

**Signal cards** expand to show two tabs:
- **Chart** — price history with EMA20 (stocks) or Bollinger Bands + RSI (crypto)
- **News** — last 14 days of company-specific headlines, fetched live from Finnhub on first open

**Design system:** dark theme with CSS custom properties (`--surface-root`, `--surface-card`, `--surface-hover`, `--accent`, semantic colours for success/warning/error). Defined in `globals.css`.

**API client:** all backend calls go through `src/lib/api.ts` with full TypeScript types matching Pydantic models (`src/lib/types.ts`).

---

## Telegram Bot

Located in `telegram/`. A standalone `python-telegram-bot` service that connects to the same Telegram group as the backend engines.

**Commands:**

| Command | Description |
|---|---|
| `/start` | Welcome message |
| `/help` | List available commands |
| `/button` | Example inline button interaction |
| `/testalert` | Send a test alert to the group |
| `/gettopicid` | Get the topic/thread ID of the current chat |

Stock and crypto alerts are sent directly by the backend engines (not this bot) using their own Telegram tokens and topic IDs.

---

## Running the Project

### Docker (recommended)

```bash
# First run — build images and start
docker compose up --build

# Subsequent runs
docker compose up -d

# After code changes — rebuild without cache
docker compose build --no-cache && docker compose up -d

# View logs
docker compose logs -f backend
docker compose logs -f frontend
```

Services:
- Dashboard: `http://localhost:3000`
- API + Swagger docs: `http://localhost:8000/docs`

---

## Development Setup

### Backend

Requires Python 3.9+. Uses `uv` for dependency management (venv at `backend/.venv`).

```bash
cd backend

# Install dependencies with uv
uv sync

# Or with pip
pip install -e .

# Activate venv
source .venv/bin/activate

# Run with hot reload
uvicorn app.main:app --reload
```

### Frontend

Requires Node.js 20+.

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
npm run build      # Production build
npm run lint       # ESLint
```

### Telegram bot

```bash
cd telegram
pip install -r requirements.txt
python bot.py
```

---

## Data Storage

All data is stored as JSON files — no database required for the core platform.

| File | Description |
|---|---|
| `backend/app/engines/stock_sniper/data/alerts.json` | Stock signal history keyed by ticker |
| `backend/app/engines/crypto_sniper/data/alerts.json` | Crypto signal history keyed by symbol |
| `backend/app/engines/news_monitor/data/news_history.json` | News articles (14-day retention); includes `ticker` field for company-specific articles |
| `backend/app/engines/market_analysis/data/analysis_cache.json` | Cached AI market analysis for stock and crypto |

Data directories are mounted as Docker volumes so data persists across container rebuilds.
