"use client";

import { useApi } from "@/hooks/useApi";
import { getStatus, getStockSignals, getNewsFeed } from "@/lib/api";
import { formatDate } from "@/lib/format";
import PageHeader from "@/components/layout/PageHeader";
import SummaryCard from "@/components/dashboard/SummaryCard";
import RecentPredictions from "@/components/dashboard/RecentPredictions";
import NewsHighlights from "@/components/dashboard/NewsHighlights";
import StatusBadge from "@/components/ui/StatusBadge";
import LoadingSkeleton from "@/components/ui/LoadingSkeleton";
import { TrendingUp, Newspaper, Settings } from "@/components/icons";

export default function Dashboard() {
  const status = useApi(getStatus);
  const signals = useApi(getStockSignals);
  const news = useApi(getNewsFeed);

  return (
    <div>
      <PageHeader title="Dashboard" />

      {status.error && (
        <div className="bg-semantic-error/10 border border-semantic-error/20 rounded-xl p-4 mb-6">
          <p className="text-sm text-semantic-error">
            Failed to connect to backend: {status.error}
          </p>
          <p className="text-xs text-text-muted mt-1">
            Make sure the backend is running on port 8000.
          </p>
        </div>
      )}

      {/* Summary cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-6">
        {signals.loading ? (
          <div className="border border-border-primary rounded-xl p-4 bg-surface-card">
            <LoadingSkeleton lines={2} />
          </div>
        ) : (
          <SummaryCard
            icon={<TrendingUp className="w-4 h-4" />}
            title="Stock Signals"
            value={signals.data?.total_alerts ?? 0}
            subtitle={`${signals.data?.unique_tickers ?? 0} unique tickers`}
          />
        )}
        {news.loading ? (
          <div className="border border-border-primary rounded-xl p-4 bg-surface-card">
            <LoadingSkeleton lines={2} />
          </div>
        ) : (
          <SummaryCard
            icon={<Newspaper className="w-4 h-4" />}
            title="News Articles"
            value={news.data?.total ?? 0}
            subtitle={`${news.data?.stock_count ?? 0} stock, ${news.data?.crypto_count ?? 0} crypto`}
          />
        )}
        {status.loading ? (
          <div className="border border-border-primary rounded-xl p-4 bg-surface-card">
            <LoadingSkeleton lines={2} />
          </div>
        ) : (
          <SummaryCard
            icon={<Settings className="w-4 h-4" />}
            title="Services"
            value={status.data?.services.filter((s) => s.running).length ?? 0}
            subtitle={`of ${status.data?.services.length ?? 0} running`}
          />
        )}
      </div>

      {/* Service status */}
      {status.data && (
        <div className="mb-6">
          <p className="text-[11px] font-medium uppercase tracking-wider text-text-muted mb-3">
            Service Status
          </p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            {status.data.services.map((service) => (
              <div
                key={service.name}
                className="border border-border-primary rounded-xl p-4 bg-surface-card"
              >
                <div className="flex justify-between items-center mb-2">
                  <h3 className="text-sm font-medium capitalize">
                    {service.name.replace("_", " ")}
                  </h3>
                  <StatusBadge status={service.running ? "running" : "stopped"} />
                </div>
                <div className="text-xs text-text-muted space-y-0.5">
                  <p>Total runs: {service.total_runs}</p>
                  <p>
                    Last run: {formatDate(service.last_run)}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Two-column: Recent predictions + News highlights */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        {signals.loading ? (
          <div className="border border-border-primary rounded-xl p-4 bg-surface-card">
            <LoadingSkeleton lines={5} />
          </div>
        ) : signals.data ? (
          <RecentPredictions alerts={signals.data.alerts} />
        ) : null}

        {news.loading ? (
          <div className="border border-border-primary rounded-xl p-4 bg-surface-card">
            <LoadingSkeleton lines={3} />
          </div>
        ) : news.data ? (
          <NewsHighlights articles={news.data.articles} />
        ) : null}
      </div>
    </div>
  );
}
