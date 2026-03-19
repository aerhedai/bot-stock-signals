# Algorithmic Financial Signal Detection with AI-Powered Market Analysis

**Project Report**
BSc Computer Science — Final Year Project
March 2026

---

## Abstract

This report describes the design and implementation of a fullstack financial signals platform that combines classical quantitative valuation strategies, real-time news monitoring, and a large language model (LLM) agent to surface actionable investment signals for retail investors. The system scans a watchlist of 436 stocks and a curated list of cryptocurrencies, delivers alerts via Telegram, and presents a live dashboard with AI-generated market analysis. The core thesis is that algorithmic approaches drawn from academic value investing literature — applied at scale with modern tooling — can provide retail investors with institutional-quality signal detection without the cost or complexity of professional systems.

---

## 1. Background and Motivation

### 1.1 The Retail Investor Problem

Retail investors have historically operated at a significant disadvantage relative to institutional counterparts. Professional asset managers employ quantitative analysts who apply statistical models across large universes of securities, run systematic screening processes, and consume structured data feeds that are inaccessible or prohibitively expensive for individuals. The rise of commission-free brokerages (Robinhood, Trading 212, Freetrade) has democratised trade execution, but the informational asymmetry in *identifying* what to trade has largely persisted.

The problem this project addresses is not trade execution but *signal generation*: how can a retail investor, without access to a Bloomberg terminal or a quant team, identify securities that a formal valuation model suggests are materially underpriced? More specifically, can a fully automated pipeline — from data acquisition through analysis to delivery — be constructed using freely available APIs and open-source tooling, and can modern LLMs add meaningful analytical value to the output?

### 1.2 Why This Problem Matters

The scale of retail participation in equity markets makes this a meaningful problem. In the United Kingdom and United States, retail investors now account for a substantial fraction of daily trading volume; estimates for US equity markets suggest retail activity reached approximately 20–25% of daily volume by 2023 [1]. Despite this participation, academic research consistently finds that retail investors underperform market indices [2], a finding typically attributed to behavioural biases and information disadvantages rather than execution costs alone.

A systematic, emotionally detached screening tool that applies consistent valuation criteria — without being subject to recency bias, overconfidence, or the disposition effect — addresses one of the core drivers of retail underperformance.

### 1.3 Project Aims

The project aimed to:

1. Implement three quantitatively grounded stock valuation strategies covering distinct time horizons and analytical frameworks.
2. Implement a technical analysis monitor for cryptocurrency assets.
3. Build a real-time news aggregation system that enriches signal context with relevant market news.
4. Deploy an LLM agent capable of synthesising signals and news into coherent market analysis.
5. Deliver all outputs through a Telegram notification system and a web-based dashboard accessible from any device.
6. Package the entire system as a containerised deployment runnable with a single command.

---

## 2. Context and Related Work

### 2.1 Value Investing and the Graham Number

The primary stock valuation method implemented in this project is the Graham Number, derived from the work of Benjamin Graham, widely regarded as the father of value investing. Graham's *Security Analysis* (1934, co-authored with David Dodd) [3] and *The Intelligent Investor* (1949) [4] established the theoretical framework for identifying securities trading below intrinsic value — what Graham termed a "margin of safety."

The Graham Number is a specific formula arising from this tradition:

$$\text{Graham Price} = \sqrt{22.5 \times \text{EPS} \times \text{Book Value Per Share}}$$

The constant 22.5 is derived from Graham's rule of thumb that a stock's P/E ratio multiplied by its price-to-book ratio should not exceed 22.5. In this implementation, a signal fires when the current market price is more than 20% below the computed Graham price — i.e., when the stock trades at a greater than 20% discount to intrinsic value. This strategy is assigned to a long-term time horizon (3–12 months), consistent with the original theoretical framing.

The relevance of Graham-style analysis remains debated. The Efficient Market Hypothesis in its semi-strong form [5] suggests that all publicly available information, including earnings and book value, is already priced in, rendering such strategies theoretically ineffective. However, a substantial body of empirical work — including Fama and French's three-factor model [6] — documents a persistent "value premium" in equity returns: stocks with low price-to-book ratios have historically outperformed. This lends empirical support to systematic value screening even if the theoretical mechanism remains contested.

### 2.2 Statistical Mean Reversion (Z-Score)

The second strategy implements Z-score analysis for short-term mean reversion signals. The Z-score measures how many standard deviations the current price is from its recent historical mean:

$$Z = \frac{P_t - \mu}{\sigma}$$

A Z-score of −2 or below indicates the price has fallen two standard deviations below its recent mean, a condition interpreted as a potential short-term oversell. This approach is rooted in the statistical arbitrage literature and the empirical observation of mean reversion in equity prices over short horizons [7]. It is assigned to a short-term time horizon (1–5 trading days).

### 2.3 Linear Regression Trend Deviation

The third strategy applies ordinary least squares regression to recent price history to identify stocks trading significantly below their linear trend. This is conceptually related to the broader literature on technical analysis and momentum, though it inverts the momentum signal: rather than following the trend, it flags departures from it as potential reversion opportunities. It is assigned to a swing trade time horizon (1–4 weeks).

The academic standing of technical analysis is mixed. Brock, Lakonishok and LeBaron [8] found evidence of technical trading rules generating significant abnormal returns in historical data, though subsequent research has questioned whether such patterns persist after transaction costs and out-of-sample.

### 2.4 Cryptocurrency Technical Analysis

Cryptocurrency markets exhibit characteristically higher volatility and are less regulated than equity markets, making technical indicators particularly prevalent among practitioners. The crypto engine implements:

- **RSI (Relative Strength Index)**: Developed by Welles Wilder [9], a momentum oscillator measuring the speed and magnitude of recent price changes. Values below 30 are conventionally interpreted as oversold conditions.
- **Bollinger Bands**: Introduced by John Bollinger [10], bands drawn at two standard deviations above and below a moving average. Price touching or breaking the lower band signals potential oversold conditions.

### 2.5 News Sentiment and Market Analysis

The role of news in financial markets is well-established. Tetlock [11] demonstrated that media pessimism predicts downward pressure on market prices and that unusually high or low levels of media sentiment predict high market trading volume. The integration of news monitoring in this project — particularly the AI-generated summaries — draws on this literature, though the implementation operates at the qualitative level (identifying themes and sentiment from headlines) rather than through formal sentiment scoring.

### 2.6 LLM Agents in Financial Applications

The use of large language models with tool-calling capabilities as autonomous agents is an emerging research area. The ReAct framework (Reasoning + Acting) [12] demonstrated that LLMs interleaved with tool invocations outperform prompting alone on complex tasks. This project implements a tool-augmented agent pattern: the LLM (Gemini 2.5 Flash) is provided with a set of callable tools — functions that read signals, news, and cached analysis — and orchestrates its own information gathering before producing a market summary.

Commercial applications in this space include Bloomberg GPT [13], a 50-billion parameter LLM trained on financial text, and various robo-advisory platforms (Betterment, Wealthfront, Nutmeg) that automate portfolio construction. This project differs from robo-advisors in that it is explicitly a *signal detection* system, not a portfolio manager: it identifies candidates for investigation without executing trades or managing allocations.

### 2.7 Existing Open-Source Tools

Several open-source projects address adjacent problems. Zipline [14], originally developed by Quantopian, provides a backtesting framework for algorithmic trading strategies. QuantLib [15] is a comprehensive quantitative finance library covering derivatives pricing and risk management. Neither provides the end-to-end pipeline — from scanning through delivery to a consumer-facing dashboard — that this project implements. The closest comparison is probably a self-hosted instance of TradingView alerts, though that system does not support custom valuation strategies or LLM-generated analysis.

---

## 3. Design and Implementation

### 3.1 System Architecture

The system is structured as a three-service monorepo deployed via Docker Compose:

```
┌─────────────────────────────────────────────────────────────┐
│  Docker Compose                                              │
│                                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────┐  │
│  │   Backend   │    │   Frontend   │    │  Telegram Bot  │  │
│  │  FastAPI    │    │   Next.js    │    │  python-tg-bot │  │
│  │  :8000      │    │   :3000      │    │                │  │
│  └──────┬──────┘    └──────┬───────┘    └───────┬────────┘  │
│         │                  │                    │           │
│         └──────────────────┴────────────────────┘           │
│                     REST API / Telegram API                  │
└─────────────────────────────────────────────────────────────┘
```

The backend is the system's core: it runs all analysis engines, manages scheduled jobs, maintains the data store, and exposes a REST API consumed by both the frontend and external integrations. The frontend is a Next.js single-page application that presents the dashboard. The Telegram bot handles interactive commands from group members.

### 3.2 The Backend Engines

#### Stock Sniper

The stock scanner runs on a one-hour cycle against a watchlist of 436 tickers organised across 16 sectors (Technology, Finance, Healthcare, Consumer, Energy/Industrials, Telecom/Utilities, Real Estate, Transportation, Materials, Semiconductors, and others). Before any strategy is evaluated, two safety filters run:

- **Market Regime Filter**: SPY (S&P 500 ETF) must be trading above its 200-day simple moving average. This prevents the system from generating long signals during structural market downturns, consistent with the literature on trend-following filters in systematic strategies.
- **Earnings Trap Filter**: Tickers with earnings announcements within three days are excluded. Earnings announcements introduce binary uncertainty that invalidates valuation-based entry assumptions.

Each passing ticker is evaluated against all three strategies independently. Signals carry a confidence score (0–100) and a time horizon classification. Only signals with a score of 60 or above are persisted and sent to Telegram.

Market data is sourced from Yahoo Finance via `yfinance`, a widely used open-source wrapper for Yahoo Finance's unofficial API. This introduces a known reliability risk: Yahoo Finance imposes rate limits that caused issues during initial development, requiring the implementation of batching and retry logic.

#### Crypto Sniper

The cryptocurrency monitor runs on a 30-minute cycle against a curated watchlist. It applies RSI, Bollinger Band, 24-hour price change, 7-day price change, and volume spike criteria. Each signal is assigned a severity level (low/medium/high/critical) and a combined confidence score synthesised from multiple indicators.

#### News Monitor

News is fetched from the Finnhub API on two tracks. General market news (category `general` and `crypto`) runs every five minutes and feeds the news page and Telegram topics. Company-specific news (Finnhub's `/company-news` endpoint) runs hourly for all tickers that have fired a signal in the preceding 30 days. This two-track approach keeps the Telegram feed focused on broad market news while building a richer per-ticker news context for the dashboard's signal panels.

News articles are retained for 14 days. On the first request for a ticker's news panel, if fewer than three cached articles exist, the system fetches live from Finnhub and caches the results — providing an immediate experience without waiting for the scheduled enrichment job.

#### Market Analysis Engine

The analysis engine runs daily and uses the LLM agent to generate 5–7 sentence market summaries for both the stock and crypto markets. The agent reads the pool of recent headlines and the existing cached analysis, then applies its own judgement about whether a refresh is warranted — only calling the write tool if the analysis is outdated or the headline pool has grown significantly. This conditional approach reduces API calls and cost.

### 3.3 The AI Agent Architecture

The AI agent uses Google's Gemini 2.5 Flash model via the Vertex AI API. The model's `thinking_budget` is set to zero, disabling extended reasoning tokens for cost efficiency on high-frequency tasks.

A central `AgentOrchestrator` singleton maintains a registry of callable tools. At startup, each engine registers its tools with the orchestrator. The orchestrator exposes a `run_task` method that accepts a natural-language task description, a subset of tool names to expose for that task, and execution parameters. The agent loop is a standard function-calling pattern: the model issues function call requests, the orchestrator executes the handlers synchronously, returns results to the model as function response parts, and the loop continues until the model issues a final text response.

Six tools are currently registered:

| Tool | Purpose |
|---|---|
| `get_market_headlines` | Read recent news headlines by category |
| `get_market_analysis` | Read the current cached market summary |
| `update_market_analysis` | Write a new summary to cache |
| `get_ticker_headlines` | Read the last 14 days of news for a specific ticker |
| `get_stock_signals` | Read recent stock sniper alerts |
| `get_crypto_signals` | Read recent crypto sniper alerts |

A hard rate limit of 20 agent calls per hour is enforced at the orchestrator level to prevent runaway API costs in the event of bugs or unexpected usage patterns.

### 3.4 Data Storage

All persistent data is stored as JSON files. Three data files are in active use:

- `alerts.json` (stock and crypto, separate files) — signal history keyed by ticker/symbol
- `news_history.json` — news articles with category, headline, URL, sent timestamp, and optional ticker
- `analysis_cache.json` — latest AI-generated analysis for each market category

This approach was chosen for simplicity and to avoid the operational overhead of a database for a single-user deployment. The files are mounted as Docker volumes, preserving data across container rebuilds. The primary limitation is that JSON files are not suited to concurrent writes, though in practice the single-process architecture (one FastAPI process, one scheduler) makes concurrent write collisions extremely unlikely.

### 3.5 Frontend

The dashboard is built with Next.js 16 and React 19, using Tailwind CSS v4 for styling and Recharts for charting. The design system uses a dark theme with CSS custom properties defining the colour palette — surface levels, text hierarchy, and semantic colours for success/warning/error states.

Key UI decisions:
- **Signal cards are expandable**, showing a Chart tab (price history with technical overlays) and a News tab (company-specific headlines). This keeps the list compact while allowing deep investigation inline.
- **The news page uses filter tabs and a search bar**, allowing users to filter by category (All/Stock/Crypto) and search across headline text, ticker symbols, and source names simultaneously.
- **The dashboard homepage is AI-orchestrated**: every request runs the agent, which assembles the full payload and writes a fresh market briefing when warranted.

### 3.6 Technology Stack Summary

| Layer | Technology | Version |
|---|---|---|
| Backend runtime | Python (via uv) | 3.14 |
| Backend framework | FastAPI | 0.110+ |
| Job scheduling | APScheduler | 3.10+ |
| Data validation | Pydantic v2 | — |
| Market data | yfinance | 0.2.36+ |
| Numerical analysis | NumPy, pandas, scikit-learn | — |
| News API | Finnhub | REST |
| AI model | Gemini 2.5 Flash (Vertex AI) | — |
| Frontend framework | Next.js | 16.1.6 |
| Frontend language | TypeScript | 5.9 |
| Styling | Tailwind CSS | v4 |
| Charts | Recharts | 3.8 |
| Containerisation | Docker Compose | — |
| Version control | Git / GitHub | — |

---

## 4. Evaluation and Conclusions

### 4.1 What Has Been Accomplished

The system delivers end-to-end automated signal detection and delivery. A user who configures the environment variables and runs `docker compose up --build` receives:

- Automated stock scans hourly across 436 tickers with three independent strategy frameworks
- Automated crypto monitoring every 30 minutes
- News delivered to Telegram topics every five minutes
- AI-written market summaries refreshed daily (or on demand)
- A live web dashboard showing all of the above with interactive signal cards, charts, and news panels
- Company-specific news for every signal ticker, surfaced inline within the signal card

The signal pipeline has been observed to fire consistently on tickers with meaningful Graham discounts (e.g. commodity and telecom stocks in periods of sector weakness), and the Z-score strategy has identified short-term oversell events following broader market drawdowns.

### 4.2 Limitations and Critical Appraisal

**Data source reliability.** The reliance on `yfinance` introduces fragility. Yahoo Finance's unofficial API has experienced rate limiting, data gaps, and occasional stale values for earnings and book value data. During development, a rate-limiting incident caused zero signals to be generated across a full watchlist scan; this was resolved by implementing per-batch delays and retry logic, but the underlying dependency on an undocumented API remains a risk. A production-grade system would use a paid, SLA-backed data provider (e.g. Polygon.io, Intrinio, or a Bloomberg data licence).

**No backtesting.** The most significant methodological gap is the absence of a formal backtesting framework. While the three strategies are grounded in academic and practitioner literature, no systematic evaluation has been performed on whether the specific parameterisations used (20% Graham discount threshold, Z-score of −2, minimum score of 60) would have generated positive risk-adjusted returns historically. This is a material limitation for any investment application and is the most important next development step.

**No ground truth for the AI analysis.** The quality of the AI-generated market summaries is difficult to evaluate rigorously. The summaries are qualitatively coherent and appear to accurately reflect the sentiment of the input headlines, but there is no formal evaluation framework (e.g. comparing agent-generated summaries against professional analyst commentary using ROUGE or BERTScore metrics).

**JSON storage scalability.** The JSON file approach is appropriate for a single-user or small-group deployment but would not scale to concurrent users or high-frequency data ingestion. A migration to a time-series database (e.g. TimescaleDB or InfluxDB) for signal and price data, and a relational database for news and analysis, would be necessary for any production deployment.

**Rate limiting on the AI agent.** The 20 calls per hour cap is conservative and can cause the dashboard to return stale analysis during periods of high usage. This is a cost management measure but represents a user experience limitation.

### 4.3 Comparison to Existing Solutions

Relative to commercial alternatives, the system occupies a distinct niche. Robo-advisors (Betterment, Wealthfront, Nutmeg) offer portfolio management automation but apply passive index strategies and do not generate individual stock selection signals. TradingView provides technical analysis tooling and alert systems but requires manual strategy configuration per ticker, does not apply fundamental valuation strategies, and does not offer integrated AI analysis. Quantopian (now defunct) and QuantConnect offer backtesting environments but not live signal delivery pipelines or AI-generated narrative analysis.

The integration of an LLM agent as a first-class component of the signal pipeline — reading structured data through tool calls and producing narrative synthesis — is a relatively novel architectural pattern in this domain. Bloomberg GPT [13] represents a much larger-scale version of this idea (a domain-specific LLM trained on financial text), but this project demonstrates that a general-purpose LLM augmented with well-designed tools can produce useful financial analysis without domain-specific fine-tuning.

### 4.4 Future Work

The most valuable extensions, in priority order, would be:

1. **Backtesting engine** — replay historical signals against price data to produce win rate statistics per strategy, sector, and time horizon.
2. **Signal Devil's Advocate** — for each fired signal, run a second agent pass that argues the bear case, providing counterbalance before the alert is sent to Telegram.
3. **Outcome tracker** — schedule follow-up checks at 2 weeks, 4 weeks, and 3 months after each signal to record whether the price moved toward the target, building a real-time track record.
4. **Ticker research agent** — on-demand, deep-dive analysis for a specific ticker, synthesising signals, news, and macro context into a structured research note.
5. **Plugin / tool store** — a credential-gated extension system allowing new data integrations (earnings calendars, options flow, insider trading, sector ETF data) to be installed and registered with the agent dynamically.

### 4.5 Conclusions

This project demonstrates that a well-architected combination of classical quantitative finance methods and modern LLM tooling can produce a practically useful retail investment signal platform, deployable on commodity hardware with freely available APIs. The three-strategy approach provides meaningful coverage of distinct investment time horizons. The AI agent adds a qualitative synthesis layer that transforms structured signal data into readable market context.

The most important finding — and the most interesting area for further investigation — is the architectural pattern of the LLM agent with a tool registry. The agent's ability to decide *whether* to refresh analysis (rather than blindly regenerating on every request) represents a form of autonomous resource management that reduces cost while maintaining quality. As tool registries expand to cover more data sources and action types, this pattern has the potential to power increasingly sophisticated financial analysis agents.

---

## References

[1] Welch, I. (2022). *The Wisdom of the Robinhood Crowd*. Journal of Finance, 77(3), 1489–1527.

[2] Barber, B.M. & Odean, T. (2000). *Trading Is Hazardous to Your Wealth: The Common Stock Investment Performance of Individual Investors*. Journal of Finance, 55(2), 773–806.

[3] Graham, B. & Dodd, D. (1934). *Security Analysis*. McGraw-Hill.

[4] Graham, B. (1949). *The Intelligent Investor*. Harper & Brothers.

[5] Fama, E.F. (1970). *Efficient Capital Markets: A Review of Empirical Work*. Journal of Finance, 25(2), 383–417.

[6] Fama, E.F. & French, K.R. (1992). *The Cross-Section of Expected Stock Returns*. Journal of Finance, 47(2), 427–465.

[7] Poterba, J.M. & Summers, L.H. (1988). *Mean Reversion in Stock Prices: Evidence and Implications*. Journal of Financial Economics, 22(1), 27–59.

[8] Brock, W., Lakonishok, J. & LeBaron, B. (1992). *Simple Technical Trading Rules and the Stochastic Properties of Stock Returns*. Journal of Finance, 47(5), 1731–1764.

[9] Wilder, J.W. (1978). *New Concepts in Technical Trading Systems*. Trend Research.

[10] Bollinger, J. (2002). *Bollinger on Bollinger Bands*. McGraw-Hill.

[11] Tetlock, P.C. (2007). *Giving Content to Investor Sentiment: The Role of Media in the Stock Market*. Journal of Finance, 62(3), 1139–1168.

[12] Yao, S., Zhao, J., Yu, D., Du, N., Shafran, I., Narasimhan, K. & Cao, Y. (2022). *ReAct: Synergizing Reasoning and Acting in Language Models*. arXiv:2210.03629.

[13] Wu, S., Irsoy, O., Lu, S., Dabravolski, V., Dredze, M., Gehrmann, S., Kambadur, P., Rosenberg, D. & Mann, G. (2023). *BloombergGPT: A Large Language Model for Finance*. arXiv:2303.17564.

[14] Quantopian Inc. (2016). *Zipline: A Pythonic Algorithmic Trading Library*. https://github.com/quantopian/zipline.

[15] Ametrano, F.M. & Ballabio, L. (2003–present). *QuantLib: A Free/Open-Source Library for Quantitative Finance*. https://www.quantlib.org.
