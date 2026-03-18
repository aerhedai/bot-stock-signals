"use client";

import { useState } from "react";
import Link from "next/link";
import { useApi } from "@/hooks/useApi";
import { getDashboard, getStatus } from "@/lib/api";
import { formatDate, formatDateShort } from "@/lib/format";
import PageHeader from "@/components/layout/PageHeader";
import LoadingSkeleton from "@/components/ui/LoadingSkeleton";
import StatusBadge from "@/components/ui/StatusBadge";
import { BrainCircuit, TrendingUp, Newspaper, Settings, ExternalLink } from "@/components/icons";
import type { DashboardStockSignal, DashboardCryptoSignal, DashboardNewsItem, MarketAnalysisResponse } from "@/lib/types";

// ---------------------------------------------------------------------------
// Sub-components
// ---------------------------------------------------------------------------

function MetricCard({
  icon,
  label,
  value,
  sub,
  href,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  sub?: string;
  href?: string;
}) {
  const inner = (
    <div className="border border-border-primary rounded-xl p-4 bg-surface-card hover:border-accent/40 transition-colors group">
      <div className="flex items-center justify-between mb-3">
        <span className="text-text-muted">{icon}</span>
        {href && (
          <span className="text-[10px] text-accent opacity-0 group-hover:opacity-100 transition-opacity">
            View →
          </span>
        )}
      </div>
      <p className="text-2xl font-bold text-text-primary">{value}</p>
      <p className="text-xs font-medium text-text-muted mt-0.5">{label}</p>
      {sub && <p className="text-[10px] text-text-muted mt-0.5">{sub}</p>}
    </div>
  );
  return href ? <Link href={href}>{inner}</Link> : inner;
}

function AiBriefingCard({
  reasoning,
  stockAnalysis,
  cryptoAnalysis,
  generatedAt,
}: {
  reasoning: string;
  stockAnalysis: MarketAnalysisResponse | null;
  cryptoAnalysis: MarketAnalysisResponse | null;
  generatedAt: string;
}) {
  const [expanded, setExpanded] = useState(false);
  const hasAnalysis = !!(stockAnalysis || cryptoAnalysis);

  return (
    <div className="border border-accent/25 rounded-xl bg-surface-card overflow-hidden">
      <div className="px-4 py-3 border-b border-accent/15 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <BrainCircuit className="w-4 h-4 text-accent" />
          <p className="text-xs font-semibold uppercase tracking-wider text-accent">
            AI Market Briefing
          </p>
        </div>
        <span className="text-[10px] text-text-muted">{formatDateShort(generatedAt)}</span>
      </div>

      <div className="px-4 pt-3 pb-4">
        <p className="text-sm text-text-secondary leading-relaxed">{reasoning}</p>

        {hasAnalysis && (
          <button
            onClick={() => setExpanded(v => !v)}
            className="mt-3 text-xs text-accent hover:underline flex items-center gap-1"
          >
            {expanded ? "Hide detailed analysis ▲" : "View detailed analysis ▼"}
          </button>
        )}

        {expanded && (
          <div className="mt-3 grid grid-cols-1 md:grid-cols-2 gap-3">
            {stockAnalysis && (
              <div className="bg-surface-root rounded-lg p-3 border border-border-subtle">
                <div className="flex items-center justify-between mb-1.5">
                  <p className="text-[10px] uppercase tracking-wider text-text-muted font-medium">
                    Stocks
                  </p>
                  <span className="text-[10px] text-text-muted">
                    {stockAnalysis.headline_count} headlines · {formatDateShort(stockAnalysis.generated_at)}
                  </span>
                </div>
                <p className="text-xs text-text-secondary leading-relaxed">
                  {stockAnalysis.analysis}
                </p>
              </div>
            )}
            {cryptoAnalysis && (
              <div className="bg-surface-root rounded-lg p-3 border border-border-subtle">
                <div className="flex items-center justify-between mb-1.5">
                  <p className="text-[10px] uppercase tracking-wider text-text-muted font-medium">
                    Crypto
                  </p>
                  <span className="text-[10px] text-text-muted">
                    {cryptoAnalysis.headline_count} headlines · {formatDateShort(cryptoAnalysis.generated_at)}
                  </span>
                </div>
                <p className="text-xs text-text-secondary leading-relaxed">
                  {cryptoAnalysis.analysis}
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function StockSignalRow({ sig }: { sig: DashboardStockSignal }) {
  const upsidePct = sig.target ? ((sig.target - sig.price) / sig.price) * 100 : null;
  const scoreColour =
    sig.score >= 75 ? "text-semantic-success" :
    sig.score >= 50 ? "text-semantic-warning" :
    "text-semantic-error";

  return (
    <div className="px-4 py-3 flex items-center justify-between gap-3">
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm font-semibold text-text-primary">{sig.ticker}</span>
          <span className="text-[10px] text-text-muted bg-surface-active px-1.5 py-0.5 rounded">
            {sig.method}
          </span>
        </div>
        <p className="text-[10px] text-text-muted mt-0.5">{formatDateShort(sig.timestamp)}</p>
      </div>
      <div className="flex items-center gap-3 text-right shrink-0">
        <div>
          <p className="text-xs text-text-muted">Entry</p>
          <p className="text-sm font-medium text-text-primary">${sig.price.toFixed(2)}</p>
        </div>
        {upsidePct !== null && (
          <div>
            <p className="text-xs text-text-muted">Upside</p>
            <p className={`text-sm font-semibold ${upsidePct >= 0 ? "text-semantic-success" : "text-semantic-error"}`}>
              {upsidePct >= 0 ? "+" : ""}{upsidePct.toFixed(1)}%
            </p>
          </div>
        )}
        <div className="text-right">
          <p className="text-xs text-text-muted">Score</p>
          <p className={`text-sm font-bold ${scoreColour}`}>{sig.score.toFixed(0)}</p>
        </div>
      </div>
    </div>
  );
}

function CryptoSignalRow({ sig }: { sig: DashboardCryptoSignal }) {
  const displaySymbol = sig.symbol.replace("-USD", "");
  return (
    <div className="px-4 py-3 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <span className="w-6 h-6 rounded-full bg-accent/10 flex items-center justify-center text-[9px] font-bold text-accent">
          {displaySymbol.slice(0, 2)}
        </span>
        <div>
          <p className="text-sm font-semibold text-text-primary">{displaySymbol}</p>
          <p className="text-[10px] text-text-muted">{sig.symbol}</p>
        </div>
      </div>
      <span className="text-[10px] text-text-muted">{formatDateShort(sig.timestamp)}</span>
    </div>
  );
}

function NewsRow({ item }: { item: DashboardNewsItem }) {
  const catColour: Record<string, string> = {
    stock: "text-accent bg-accent/10",
    crypto: "text-semantic-warning bg-semantic-warning/10",
  };
  const cls = catColour[item.category?.toLowerCase()] ?? "text-text-muted bg-surface-active";

  return (
    <div className="px-4 py-3 flex items-start justify-between gap-3">
      <div className="min-w-0 flex-1">
        <p className="text-sm text-text-primary line-clamp-2 leading-snug">{item.headline}</p>
        <div className="flex items-center gap-2 mt-1">
          <span className={`text-[9px] uppercase tracking-wider font-semibold px-1.5 py-0.5 rounded ${cls}`}>
            {item.category}
          </span>
          <span className="text-[10px] text-text-muted">{formatDateShort(item.sent_at)}</span>
        </div>
      </div>
      {item.url && (
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-text-muted hover:text-accent shrink-0 mt-0.5"
        >
          <ExternalLink className="w-3.5 h-3.5" />
        </a>
      )}
    </div>
  );
}

function SectionCard({
  title,
  href,
  children,
  empty,
}: {
  title: string;
  href?: string;
  children: React.ReactNode;
  empty?: string;
}) {
  return (
    <div className="border border-border-primary rounded-xl bg-surface-card overflow-hidden">
      <div className="flex items-center justify-between px-4 py-3 border-b border-border-subtle">
        <p className="text-xs font-medium uppercase tracking-wider text-text-muted">{title}</p>
        {href && (
          <Link href={href} className="text-xs text-accent hover:underline">
            View all →
          </Link>
        )}
      </div>
      {children}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Main page
// ---------------------------------------------------------------------------

export default function Dashboard() {
  const dashboard = useApi(getDashboard);
  const status = useApi(getStatus);

  const d = dashboard.data;

  return (
    <div>
      <PageHeader title="Dashboard" />

      {/* Backend error banner */}
      {dashboard.error && (
        <div className="bg-semantic-error/10 border border-semantic-error/20 rounded-xl p-4 mb-6">
          <p className="text-sm text-semantic-error font-medium">
            Failed to load dashboard
          </p>
          <p className="text-xs text-text-muted mt-1">
            {dashboard.error} — make sure the backend is running on port 8000.
          </p>
        </div>
      )}

      {/* Metric cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        {dashboard.loading ? (
          Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="border border-border-primary rounded-xl p-4 bg-surface-card">
              <LoadingSkeleton lines={2} />
            </div>
          ))
        ) : (
          <>
            <MetricCard
              icon={<TrendingUp className="w-4 h-4" />}
              label="Stock Signals"
              value={d?.stock_signals.length ?? 0}
              sub="active predictions"
              href="/predictions/stocks"
            />
            <MetricCard
              icon={<TrendingUp className="w-4 h-4" />}
              label="Crypto Signals"
              value={d?.crypto_signals.length ?? 0}
              sub="active predictions"
              href="/predictions/crypto"
            />
            <MetricCard
              icon={<Newspaper className="w-4 h-4" />}
              label="News Articles"
              value={d?.news.length ?? 0}
              sub="in feed"
              href="/news"
            />
            <MetricCard
              icon={<Settings className="w-4 h-4" />}
              label="Services"
              value={
                status.data
                  ? `${status.data.services.filter(s => s.running).length}/${status.data.services.length}`
                  : "—"
              }
              sub="running"
            />
          </>
        )}
      </div>

      {/* AI Briefing */}
      {dashboard.loading ? (
        <div className="border border-border-primary rounded-xl p-4 bg-surface-card mb-6">
          <LoadingSkeleton lines={4} />
        </div>
      ) : d ? (
        <div className="mb-6">
          <AiBriefingCard
            reasoning={d.agent_reasoning}
            stockAnalysis={d.stock_analysis}
            cryptoAnalysis={d.crypto_analysis}
            generatedAt={d.generated_at}
          />
        </div>
      ) : null}

      {/* Signals row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 mb-6">
        {/* Stock signals */}
        {dashboard.loading ? (
          <div className="border border-border-primary rounded-xl p-4 bg-surface-card">
            <LoadingSkeleton lines={5} />
          </div>
        ) : d ? (
          <SectionCard title="Recent Stock Signals" href="/predictions/stocks">
            {d.stock_signals.length === 0 ? (
              <p className="px-4 py-6 text-sm text-text-muted text-center">
                No signals yet. Run a scan to populate predictions.
              </p>
            ) : (
              <div className="divide-y divide-border-subtle">
                {d.stock_signals.slice(0, 5).map((sig) => (
                  <StockSignalRow key={`${sig.ticker}-${sig.timestamp}`} sig={sig} />
                ))}
              </div>
            )}
          </SectionCard>
        ) : null}

        {/* Crypto signals */}
        {dashboard.loading ? (
          <div className="border border-border-primary rounded-xl p-4 bg-surface-card">
            <LoadingSkeleton lines={5} />
          </div>
        ) : d ? (
          <SectionCard title="Recent Crypto Signals" href="/predictions/crypto">
            {d.crypto_signals.length === 0 ? (
              <p className="px-4 py-6 text-sm text-text-muted text-center">
                No signals yet. Run a scan to populate predictions.
              </p>
            ) : (
              <div className="divide-y divide-border-subtle">
                {d.crypto_signals.slice(0, 5).map((sig) => (
                  <CryptoSignalRow key={sig.symbol} sig={sig} />
                ))}
              </div>
            )}
          </SectionCard>
        ) : null}
      </div>

      {/* News + Service status row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        {/* News */}
        {dashboard.loading ? (
          <div className="border border-border-primary rounded-xl p-4 bg-surface-card">
            <LoadingSkeleton lines={4} />
          </div>
        ) : d ? (
          <SectionCard title="News Highlights" href="/news">
            {d.news.length === 0 ? (
              <p className="px-4 py-6 text-sm text-text-muted text-center">
                No news articles yet.
              </p>
            ) : (
              <div className="divide-y divide-border-subtle">
                {d.news.slice(0, 4).map((item, i) => (
                  <NewsRow key={i} item={item} />
                ))}
              </div>
            )}
          </SectionCard>
        ) : null}

        {/* Service status */}
        <div className="border border-border-primary rounded-xl bg-surface-card overflow-hidden">
          <div className="px-4 py-3 border-b border-border-subtle">
            <p className="text-xs font-medium uppercase tracking-wider text-text-muted">
              Service Status
            </p>
          </div>
          {status.loading ? (
            <div className="p-4">
              <LoadingSkeleton lines={4} />
            </div>
          ) : status.error ? (
            <p className="px-4 py-4 text-sm text-semantic-error">
              Could not load service status.
            </p>
          ) : status.data ? (
            <div className="divide-y divide-border-subtle">
              {status.data.services.map((svc) => (
                <div key={svc.name} className="px-4 py-3 flex items-center justify-between gap-3">
                  <div className="min-w-0">
                    <p className="text-sm font-medium capitalize text-text-primary">
                      {svc.name.replace(/_/g, " ")}
                    </p>
                    <p className="text-[10px] text-text-muted mt-0.5">
                      Last run: {formatDate(svc.last_run)} · {svc.total_runs} total
                    </p>
                  </div>
                  <StatusBadge status={svc.running ? "running" : "stopped"} />
                </div>
              ))}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
