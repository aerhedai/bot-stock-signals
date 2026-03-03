"use client";

import { useApi } from "@/hooks/useApi";
import { getCryptoSignals, getCryptoWatchlist, triggerCryptoScan } from "@/lib/api";
import { formatDateShort } from "@/lib/format";
import PageHeader from "@/components/layout/PageHeader";
import LoadingSkeleton from "@/components/ui/LoadingSkeleton";
import EmptyState from "@/components/ui/EmptyState";
import { TrendingUp } from "@/components/icons";
import { useState } from "react";

export default function CryptoPredictionsPage() {
  const signals = useApi(getCryptoSignals);
  const watchlist = useApi(getCryptoWatchlist);
  const [scanning, setScanning] = useState(false);
  const [scanMsg, setScanMsg] = useState("");

  const handleScan = async () => {
    setScanning(true);
    setScanMsg("");
    try {
      const result = await triggerCryptoScan();
      setScanMsg(result.message);
      signals.refetch();
    } catch {
      setScanMsg("Scan failed.");
    } finally {
      setScanning(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="Crypto Predictions"
        action={
          <button
            onClick={handleScan}
            disabled={scanning}
            className="px-3 py-1.5 bg-accent text-white rounded-lg hover:bg-accent-hover disabled:opacity-50 text-sm transition-colors"
          >
            {scanning ? "Scanning..." : "Run Scan"}
          </button>
        }
      />

      {scanMsg && (
        <p className="text-sm text-semantic-success mb-4">{scanMsg}</p>
      )}

      <section className="mb-8">
        <p className="text-[11px] font-medium uppercase tracking-wider text-text-muted mb-3">
          Alert History
        </p>
        {signals.loading && <LoadingSkeleton lines={4} />}
        {signals.error && <p className="text-semantic-error text-sm">{signals.error}</p>}
        {signals.data && (
          <div>
            <p className="text-sm text-text-secondary mb-2">
              {signals.data.total_alerts} total alerts
            </p>
            {Object.keys(signals.data.alerts).length === 0 ? (
              <EmptyState
                icon={<TrendingUp className="w-8 h-8" />}
                message="No alerts recorded yet."
              />
            ) : (
              <div className="space-y-2">
                {Object.entries(signals.data.alerts).map(([symbol, ts]) => (
                  <div
                    key={symbol}
                    className="flex justify-between items-center border border-border-primary rounded-xl p-3 bg-surface-card"
                  >
                    <span className="font-medium text-sm">{symbol}</span>
                    <span className="text-xs text-text-secondary">{formatDateShort(ts)}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </section>

      <section>
        <p className="text-[11px] font-medium uppercase tracking-wider text-text-muted mb-3">
          Watchlist
        </p>
        {watchlist.loading && <LoadingSkeleton lines={3} />}
        {watchlist.error && <p className="text-semantic-error text-sm">{watchlist.error}</p>}
        {watchlist.data && (
          <div>
            <p className="text-sm text-text-secondary mb-3">
              {watchlist.data.total} cryptocurrencies
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {Object.entries(watchlist.data.categories).map(
                ([category, symbols]) => (
                  <div
                    key={category}
                    className="border border-border-primary rounded-xl p-3 bg-surface-card"
                  >
                    <h3 className="text-sm font-medium mb-1">{category}</h3>
                    <p className="text-xs text-text-muted">
                      {symbols.join(", ")}
                    </p>
                  </div>
                )
              )}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
