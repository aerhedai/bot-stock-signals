"use client";

import { useApi } from "@/hooks/useApi";
import { getStockSignals, getStockWatchlist, triggerStockScan } from "@/lib/api";
import SignalTable from "@/components/signals/SignalTable";
import PageHeader from "@/components/layout/PageHeader";
import LoadingSkeleton from "@/components/ui/LoadingSkeleton";
import ScanOverlay from "@/components/ui/ScanOverlay";
import { useState } from "react";

export default function StockPredictionsPage() {
  const signals = useApi(getStockSignals);
  const watchlist = useApi(getStockWatchlist);
  const [scanning, setScanning] = useState(false);
  const [scanMsg, setScanMsg] = useState("");

  const handleScan = async () => {
    setScanning(true);
    setScanMsg("");
    try {
      const result = await triggerStockScan();
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
        title="Stock Predictions"
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
          Predictions
        </p>
        {signals.loading && <LoadingSkeleton lines={4} />}
        {signals.error && <p className="text-semantic-error text-sm">{signals.error}</p>}
        {signals.data && <SignalTable alerts={signals.data.alerts} />}
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
              {watchlist.data.total} tickers across{" "}
              {Object.keys(watchlist.data.sectors).length} sectors
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {Object.entries(watchlist.data.sectors).map(([sector, tickers]) => (
                <div
                  key={sector}
                  className="border border-border-primary rounded-xl p-3 bg-surface-card"
                >
                  <h3 className="text-sm font-medium mb-1">{sector}</h3>
                  <p className="text-xs text-text-muted">
                    {tickers.length} tickers
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>

      {scanning && (
        <ScanOverlay
          title="Scanning Stocks…"
          subtitle="Analysing tickers against valuation strategies. This takes a few minutes."
        />
      )}
    </div>
  );
}
