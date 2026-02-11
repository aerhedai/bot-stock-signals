# Telegram Signals Bot

A fullstack monorepo for financial market analysis and Telegram alerts. Includes stock valuation scanning, crypto monitoring, and news aggregation — with a FastAPI backend, Next.js dashboard, and Telegram bot.

## Architecture

```
bot-telegram-signals/
├── backend/          # FastAPI API + analysis engines
│   ├── app/
│   │   ├── api/      # REST endpoints (/api/v1/...)
│   │   ├── models/   # Pydantic response schemas
│   │   ├── services/ # Scheduler, alert store
│   │   └── engines/  # Analysis modules
│   │       ├── stock_sniper/   # Stock valuation scanner
│   │       ├── crypto_sniper/  # Crypto monitor
│   │       └── news_monitor/   # Finnhub news fetcher
│   ├── pyproject.toml
│   └── Dockerfile
│
├── frontend/         # Next.js dashboard (TypeScript, Tailwind)
│   ├── src/app/      # Pages: dashboard, stocks, crypto, news, settings
│   ├── src/components/
│   └── Dockerfile
│
├── telegram/         # Telegram bot service
│   ├── bot.py
│   ├── handlers/
│   └── Dockerfile
│
├── tools/            # CLI utilities (ticker management)
├── docker-compose.yml
└── .env              # All configuration (not tracked)
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 20+
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A Finnhub API key from [finnhub.io](https://finnhub.io/register)

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env with your tokens and IDs
```

### 2. Run with Docker (recommended)

```bash
docker compose up --build
```

This starts three services:
- **Backend** at `http://localhost:8000` (API docs at `/docs`)
- **Frontend** at `http://localhost:3000`
- **Telegram bot** (connects to Telegram API)

### 3. Run Locally (development)

**Backend:**
```bash
cd backend
pip install -e .
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

**Telegram bot:**
```bash
cd telegram
pip install -r requirements.txt
python bot.py
```

## API Endpoints

All endpoints are documented at `http://localhost:8000/docs` (Swagger UI).

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/health/status` | Detailed status with scheduler stats |
| GET | `/api/v1/stocks/signals` | Stock alert history |
| GET | `/api/v1/stocks/watchlist` | Stock watchlist by sector |
| POST | `/api/v1/stocks/scan` | Trigger stock scan |
| GET | `/api/v1/crypto/signals` | Crypto alert history |
| GET | `/api/v1/crypto/watchlist` | Crypto watchlist |
| POST | `/api/v1/crypto/scan` | Trigger crypto scan |
| GET | `/api/v1/news/feed` | Recent news articles |
| POST | `/api/v1/news/fetch` | Trigger news fetch |

## Telegram Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | Available commands |
| `/button` | Example inline button |
| `/testalert` | Send test alert to group |
| `/gettopicid` | Get topic ID for group chats |

## Configuration

All configuration is in the root `.env` file. See `.env.example` for all available options:

- **BOT_TOKEN** — Telegram bot token
- **GROUP_CHAT_ID** — Telegram group for alerts
- **FINNHUB_API_KEY** — News API key
- **STOCK_NEWS_TOPIC_ID / CRYPTO_NEWS_TOPIC_ID** — Telegram topic IDs
- **NEWS_FETCH_INTERVAL** — News fetch interval in seconds
- **LOG_LEVEL** — Logging verbosity
