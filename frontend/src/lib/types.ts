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
  score: number;
  price: number;
  target: number | null;
  timestamp: string;
}

export interface StockAlertHistory {
  total_alerts: number;
  unique_tickers: number;
  alerts: Record<string, StockSignal[]>;
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
  trigger_type: string;
  severity: string;
  combined_score: number;
  timestamp: string;
}

export interface CryptoWatchlistResponse {
  total: number;
  categories: Record<string, string[]>;
}

export interface CryptoAlertHistory {
  total_alerts: number;
  alerts: Record<string, string>;
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
