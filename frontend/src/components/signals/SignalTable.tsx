"use client";

import { useState, useMemo } from "react";
import type { StockSignal } from "@/lib/types";
import { formatDateShort } from "@/lib/format";
import StockDetailChart from "@/components/charts/StockDetailChart";

type SortKey = "score_desc" | "score_asc" | "date_desc" | "date_asc" | "ticker_asc";

interface Props {
  alerts: Record<string, StockSignal>;
}

function ScoreBadge({ score }: { score: number }) {
  const colour =
    score >= 75
      ? "bg-semantic-success/15 text-semantic-success"
      : score >= 50
      ? "bg-semantic-warning/15 text-semantic-warning"
      : "bg-semantic-error/15 text-semantic-error";
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold ${colour}`}>
      {score.toFixed(1)}
    </span>
  );
}

function HorizonBadge({ horizon }: { horizon: string }) {
  const lower = horizon.toLowerCase();
  const colour = lower.includes("short")
    ? "bg-accent/15 text-accent"
    : lower.includes("swing")
    ? "bg-purple-500/15 text-purple-400"
    : "bg-emerald-500/15 text-emerald-400";
  const label = lower.includes("short")
    ? "Short-Term"
    : lower.includes("swing")
    ? "Swing"
    : "Long-Term";
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${colour}`}>
      {label}
    </span>
  );
}

function ChevronIcon({ open }: { open: boolean }) {
  return (
    <svg
      className={`w-4 h-4 text-text-muted transition-transform duration-200 ${open ? "rotate-180" : ""}`}
      fill="none" viewBox="0 0 24 24" stroke="currentColor"
    >
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
    </svg>
  );
}

function StockSignalCard({ sig }: { sig: StockSignal }) {
  const [expanded, setExpanded] = useState(false);

  const upside =
    sig.target && sig.price > 0
      ? ((sig.target - sig.price) / sig.price) * 100
      : null;

  return (
    <div className="border border-border-primary rounded-xl bg-surface-card overflow-hidden">
      {/* Clickable card header */}
      <button
        className="w-full text-left p-4 hover:bg-surface-hover transition-colors"
        onClick={() => setExpanded(v => !v)}
      >
        {/* Header row */}
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-base font-bold text-text-primary">{sig.ticker}</span>
            <HorizonBadge horizon={sig.time_horizon} />
            <span className="text-xs text-text-muted bg-surface-active px-2 py-0.5 rounded">
              {sig.method}
            </span>
          </div>
          <div className="flex items-center gap-2">
            <ScoreBadge score={sig.score} />
            <ChevronIcon open={expanded} />
          </div>
        </div>

        {/* Price row */}
        <div className="flex items-center gap-4 mb-2 text-sm">
          <div>
            <span className="text-text-muted text-xs">Price</span>
            <p className="font-semibold text-text-primary">${sig.price.toFixed(2)}</p>
          </div>
          {sig.target && (
            <>
              <div className="text-text-muted">→</div>
              <div>
                <span className="text-text-muted text-xs">Target</span>
                <p className="font-semibold text-text-primary">
                  ${sig.target.toFixed(2)}
                  {upside !== null && (
                    <span className={`ml-1 text-xs font-medium ${upside >= 0 ? "text-semantic-success" : "text-semantic-error"}`}>
                      ({upside >= 0 ? "+" : ""}{upside.toFixed(1)}%)
                    </span>
                  )}
                </p>
              </div>
            </>
          )}
          {sig.ema_value && (
            <div className="ml-auto text-right">
              <span className="text-text-muted text-xs">EMA(20)</span>
              <p className="text-sm text-text-secondary">${sig.ema_value.toFixed(2)}</p>
            </div>
          )}
        </div>

        {/* Reason */}
        {sig.reason && (
          <p className="text-xs text-text-secondary leading-relaxed border-t border-border-subtle pt-2 mt-2 line-clamp-2">
            {sig.reason}
          </p>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between mt-2 pt-2 border-t border-border-subtle">
          <span className="text-xs text-text-muted">{sig.time_horizon}</span>
          <span className="text-xs text-text-muted">{formatDateShort(sig.timestamp)}</span>
        </div>
      </button>

      {/* Expandable chart section */}
      {expanded && (
        <div className="px-4 pb-4 border-t border-border-subtle bg-surface-card">
          <StockDetailChart
            ticker={sig.ticker}
            targetPrice={sig.target}
            entryPrice={sig.price}
            signalTimestamp={sig.timestamp}
            timeHorizon={sig.time_horizon}
          />
        </div>
      )}
    </div>
  );
}

export default function SignalTable({ alerts }: Props) {
  const [sort, setSort] = useState<SortKey>("score_desc");

  const entries = useMemo(() => {
    const list = Object.values(alerts);
    return [...list].sort((a, b) => {
      switch (sort) {
        case "score_desc": return b.score - a.score;
        case "score_asc":  return a.score - b.score;
        case "date_desc":  return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
        case "date_asc":   return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
        case "ticker_asc": return a.ticker.localeCompare(b.ticker);
        default: return 0;
      }
    });
  }, [alerts, sort]);

  if (entries.length === 0) {
    return (
      <p className="text-text-muted text-sm py-4">
        No signals recorded yet. Run a scan to populate predictions.
      </p>
    );
  }

  return (
    <div>
      {/* Sort controls */}
      <div className="flex items-center gap-2 mb-4">
        <span className="text-xs text-text-muted">Sort by</span>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value as SortKey)}
          className="text-xs bg-surface-card border border-border-primary rounded-lg px-2 py-1 text-text-secondary focus:outline-none focus:border-accent"
        >
          <option value="score_desc">Score — high to low</option>
          <option value="score_asc">Score — low to high</option>
          <option value="date_desc">Date — newest first</option>
          <option value="date_asc">Date — oldest first</option>
          <option value="ticker_asc">Ticker — A to Z</option>
        </select>
        <span className="text-xs text-text-muted ml-auto">{entries.length} signal{entries.length !== 1 ? "s" : ""}</span>
      </div>

      {/* Signal cards */}
      <div className="space-y-3">
        {entries.map((sig) => (
          <StockSignalCard key={sig.ticker} sig={sig} />
        ))}
      </div>
    </div>
  );
}
