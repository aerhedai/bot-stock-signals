"use client";

import { useState, useMemo } from "react";
import type { CryptoSignal } from "@/lib/types";
import { formatDateShort } from "@/lib/format";

type SortKey = "score_desc" | "score_asc" | "date_desc" | "date_asc" | "symbol_asc";

interface Props {
  alerts: Record<string, CryptoSignal>;
}

function SeverityBadge({ severity }: { severity: string }) {
  const styles: Record<string, string> = {
    critical: "bg-semantic-error/15 text-semantic-error",
    high:     "bg-semantic-warning/15 text-semantic-warning",
    medium:   "bg-accent/15 text-accent",
    low:      "bg-surface-active text-text-secondary",
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold uppercase tracking-wide ${styles[severity] ?? styles.low}`}>
      {severity}
    </span>
  );
}

function ScoreBadge({ score }: { score: number }) {
  const colour =
    score >= 75
      ? "text-semantic-success"
      : score >= 50
      ? "text-semantic-warning"
      : "text-semantic-error";
  return (
    <span className={`text-lg font-bold ${colour}`}>
      {score.toFixed(1)}
      <span className="text-xs text-text-muted font-normal">/100</span>
    </span>
  );
}

function ChangeChip({ label, value }: { label: string; value: number | null }) {
  if (value === null) return null;
  const positive = value >= 0;
  return (
    <div className="text-center">
      <p className="text-[10px] text-text-muted mb-0.5">{label}</p>
      <p className={`text-xs font-semibold ${positive ? "text-semantic-success" : "text-semantic-error"}`}>
        {positive ? "+" : ""}{value.toFixed(2)}%
      </p>
    </div>
  );
}

export default function CryptoSignalCards({ alerts }: Props) {
  const [sort, setSort] = useState<SortKey>("score_desc");

  const entries = useMemo(() => {
    const list = Object.values(alerts);
    return [...list].sort((a, b) => {
      switch (sort) {
        case "score_desc": return b.combined_score - a.combined_score;
        case "score_asc":  return a.combined_score - b.combined_score;
        case "date_desc":  return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
        case "date_asc":   return new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
        case "symbol_asc": return a.symbol.localeCompare(b.symbol);
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
          <option value="symbol_asc">Symbol — A to Z</option>
        </select>
        <span className="text-xs text-text-muted ml-auto">{entries.length} signal{entries.length !== 1 ? "s" : ""}</span>
      </div>

      {/* Signal cards */}
      <div className="space-y-3">
        {entries.map((sig) => (
          <div
            key={sig.symbol}
            className="border border-border-primary rounded-xl p-4 bg-surface-card hover:bg-surface-hover transition-colors"
          >
            {/* Header */}
            <div className="flex items-start justify-between gap-3 mb-3">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="text-base font-bold text-text-primary">
                  {sig.name}
                </span>
                <span className="text-xs text-text-muted">{sig.symbol.replace("-USD", "")}</span>
                <span className="text-xs text-text-muted bg-surface-active px-2 py-0.5 rounded">
                  {sig.category}
                </span>
                <SeverityBadge severity={sig.severity} />
              </div>
              <ScoreBadge score={sig.combined_score} />
            </div>

            {/* Price + fair value */}
            <div className="flex items-center gap-4 mb-3 text-sm">
              <div>
                <span className="text-text-muted text-xs">Price</span>
                <p className="font-semibold text-text-primary">
                  ${sig.current_price.toLocaleString(undefined, { maximumFractionDigits: 4 })}
                </p>
              </div>
              {sig.fair_value_estimate && (
                <>
                  <div className="text-text-muted">→</div>
                  <div>
                    <span className="text-text-muted text-xs">Fair Value</span>
                    <p className="font-semibold text-text-primary">
                      ${sig.fair_value_estimate.toLocaleString(undefined, { maximumFractionDigits: 4 })}
                      {sig.discount_percentage !== null && (
                        <span className="ml-1 text-xs font-medium text-semantic-success">
                          ({sig.discount_percentage.toFixed(1)}% disc.)
                        </span>
                      )}
                    </p>
                  </div>
                </>
              )}
            </div>

            {/* Method + trigger */}
            <div className="grid grid-cols-2 gap-2 mb-3 text-xs">
              <div className="bg-surface-root rounded-lg px-3 py-2">
                <p className="text-text-muted mb-0.5">Valuation</p>
                <p className="font-medium text-text-primary">{sig.valuation_method}</p>
                <p className="text-text-muted">Score: {sig.valuation_score.toFixed(1)}</p>
              </div>
              <div className="bg-surface-root rounded-lg px-3 py-2">
                <p className="text-text-muted mb-0.5">Trigger</p>
                <p className="font-medium text-text-primary capitalize">{sig.trigger_type.replace(/_/g, " ")}</p>
                {sig.trigger_description && (
                  <p className="text-text-muted truncate">{sig.trigger_description}</p>
                )}
              </div>
            </div>

            {/* Technical row */}
            <div className="flex items-center gap-4 flex-wrap border-t border-border-subtle pt-3">
              {sig.rsi !== null && (
                <div className="text-center">
                  <p className="text-[10px] text-text-muted mb-0.5">RSI</p>
                  <p className={`text-xs font-semibold ${
                    sig.rsi <= 30 ? "text-semantic-success" :
                    sig.rsi >= 70 ? "text-semantic-error" :
                    "text-text-secondary"
                  }`}>
                    {sig.rsi.toFixed(1)}
                  </p>
                </div>
              )}
              {sig.bollinger_position && (
                <div className="text-center">
                  <p className="text-[10px] text-text-muted mb-0.5">Bollinger</p>
                  <p className="text-xs font-medium text-text-secondary capitalize">
                    {sig.bollinger_position.replace(/_/g, " ")}
                  </p>
                </div>
              )}
              <ChangeChip label="24 h" value={sig.change_24h} />
              <ChangeChip label="7 d" value={sig.change_7d} />
              <span className="text-xs text-text-muted ml-auto">{formatDateShort(sig.timestamp)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
