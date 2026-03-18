// Types matching backend Pydantic models

export interface HealthResponse {
  status: string;
  timestamp: string;
}

export interface ServiceStatus {
  name: string;
  running: boolean;
  last_run: string | null;
  next_run: string | null;
  total_runs: number;
}

export interface ServiceStatusResponse {
  status: string;
  timestamp: string;
  services: ServiceStatus[];
}

export interface ScanResultResponse {
  service: string;
  triggered: boolean;
  message: string;
  timestamp: string;
}

export interface StockSignal {
  ticker: string;
  method: string;
  time_horizon: string;
  score: number;
  price: number;
  target: number | null;
  reason: string;
  ema_value: number | null;
  timestamp: string;
}

export interface StockAlertHistory {
  total_alerts: number;
  unique_tickers: number;
  alerts: Record<string, StockSignal>;
}

export interface WatchlistResponse {
  total: number;
  sectors: Record<string, string[]>;
}

export interface CryptoSignal {
  symbol: string;
  name: string;
  category: string;
  current_price: number;
  valuation_method: string;
  valuation_score: number;
  fair_value_estimate: number | null;
  discount_percentage: number | null;
  trigger_type: string;
  trigger_description: string;
  rsi: number | null;
  bollinger_position: string | null;
  change_24h: number | null;
  change_7d: number | null;
  severity: string;
  confidence: string;
  combined_score: number;
  timestamp: string;
}

export interface CryptoWatchlistResponse {
  total: number;
  categories: Record<string, string[]>;
}

export interface CryptoAlertHistory {
  total_alerts: number;
  alerts: Record<string, CryptoSignal>;
}

export interface NewsArticle {
  id: string;
  headline: string;
  summary: string;
  source: string;
  url: string;
  category: string;
  sent_at: string;
}

export interface NewsFeedResponse {
  total: number;
  stock_count: number;
  crypto_count: number;
  articles: NewsArticle[];
}

export interface MarketAnalysisResponse {
  category: string;
  analysis: string;
  headline_count: number;
  generated_at: string;
}

export interface AnalysisTriggerResponse {
  triggered: boolean;
  message: string;
}

export interface StockChartPoint {
  date: string;
  price: number;
  ema20: number | null;
}

export interface StockChartData {
  ticker: string;
  data: StockChartPoint[];
  target_price: number | null;
  signal_date: string | null;
  signal_price: number | null;
}

export interface CryptoChartPoint {
  date: string;
  price: number;
  bb_upper: number | null;
  bb_mid: number | null;
  bb_lower: number | null;
  rsi: number | null;
}

export interface CryptoChartData {
  symbol: string;
  data: CryptoChartPoint[];
  fair_value: number | null;
  signal_date: string | null;
  signal_price: number | null;
}

export interface DashboardStockSignal {
  ticker: string;
  method: string;
  score: number;
  price: number;
  target: number | null;
  timestamp: string;
}

export interface DashboardCryptoSignal {
  symbol: string;
  timestamp: string;
}

export interface DashboardNewsItem {
  headline: string;
  category: string;
  sent_at: string;
  url: string;
}

export interface DashboardResponse {
  generated_at: string;
  agent_reasoning: string;
  stock_signals: DashboardStockSignal[];
  crypto_signals: DashboardCryptoSignal[];
  news: DashboardNewsItem[];
  stock_analysis: MarketAnalysisResponse | null;
  crypto_analysis: MarketAnalysisResponse | null;
}

export interface AiInsightResponse {
  ticker: string;
  insight: string;
  generated_at: string;
}
