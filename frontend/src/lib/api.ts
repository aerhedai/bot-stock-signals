// Typed fetch wrapper for /api/v1/* endpoints

import type {
  HealthResponse,
  ServiceStatusResponse,
  ScanResultResponse,
  StockAlertHistory,
  WatchlistResponse,
  CryptoAlertHistory,
  CryptoWatchlistResponse,
  NewsFeedResponse,
  TickerNewsFeedResponse,
  MarketAnalysisResponse,
  AnalysisTriggerResponse,
  StockChartData,
  CryptoChartData,
  DashboardResponse,
  AiInsightResponse,
} from "./types";


const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchApi<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) throw new Error(`API error: ${res.status} ${res.statusText}`);
  return res.json() as Promise<T>;
}

// Health
export const getHealth = () => fetchApi<HealthResponse>("/api/v1/health");
export const getStatus = () =>
  fetchApi<ServiceStatusResponse>("/api/v1/health/status");

// Stocks
export const getStockSignals = () =>
  fetchApi<StockAlertHistory>("/api/v1/stocks/signals");
export const getStockChart = (ticker: string) =>
  fetchApi<StockChartData>(`/api/v1/stocks/chart/${ticker}`);
export const getStockWatchlist = () =>
  fetchApi<WatchlistResponse>("/api/v1/stocks/watchlist");
export const triggerStockScan = () =>
  fetchApi<ScanResultResponse>("/api/v1/stocks/scan", { method: "POST" });

// Crypto
export const getCryptoSignals = () =>
  fetchApi<CryptoAlertHistory>("/api/v1/crypto/signals");
export const getCryptoChart = (symbol: string) =>
  fetchApi<CryptoChartData>(`/api/v1/crypto/chart/${encodeURIComponent(symbol)}`);
export const getCryptoWatchlist = () =>
  fetchApi<CryptoWatchlistResponse>("/api/v1/crypto/watchlist");
export const triggerCryptoScan = () =>
  fetchApi<ScanResultResponse>("/api/v1/crypto/scan", { method: "POST" });

// News
export const getNewsFeed = () =>
  fetchApi<NewsFeedResponse>("/api/v1/news/feed");
export const getTickerNews = (ticker: string) =>
  fetchApi<TickerNewsFeedResponse>(`/api/v1/news/ticker/${encodeURIComponent(ticker)}`);
export const triggerNewsFetch = () =>
  fetchApi<ScanResultResponse>("/api/v1/news/fetch", { method: "POST" });

// Market Analysis
export const getStockAnalysis = () =>
  fetchApi<MarketAnalysisResponse>("/api/v1/analysis/stocks");
export const getCryptoAnalysis = () =>
  fetchApi<MarketAnalysisResponse>("/api/v1/analysis/crypto");
export const triggerAnalysis = () =>
  fetchApi<AnalysisTriggerResponse>("/api/v1/analysis/trigger", { method: "POST" });

// Dashboard (single unified endpoint)
export const getDashboard = () =>
  fetchApi<DashboardResponse>("/api/v1/dashboard");

// AI Insights
export const getStockAiInsight = (ticker: string) =>
  fetchApi<AiInsightResponse>(`/api/v1/stocks/ai-insight/${ticker}`);
export const getCryptoAiInsight = (symbol: string) =>
  fetchApi<AiInsightResponse>(`/api/v1/crypto/ai-insight/${encodeURIComponent(symbol)}`);
