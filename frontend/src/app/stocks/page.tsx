"use client";

import { useApi } from "@/hooks/useApi";
import { getStockSignals, getStockWatchlist, triggerStockScan } from "@/lib/api";
import SignalTable from "@/components/signals/SignalTable";
import { useState } from "react";

export default function StocksPage() {
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
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Stock Signals</h1>
        <button
          onClick={handleScan}
          disabled={scanning}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm"
        >
          {scanning ? "Scanning..." : "Run Scan"}
        </button>
      </div>

      {scanMsg && (
        <p className="text-sm text-green-400 mb-4">{scanMsg}</p>
      )}

      <section className="mb-8">
        <h2 className="text-lg font-semibold mb-3">Signal History</h2>
        {signals.loading && <p className="text-gray-400 text-sm">Loading...</p>}
        {signals.error && <p className="text-red-400 text-sm">{signals.error}</p>}
        {signals.data && <SignalTable alerts={signals.data.alerts} />}
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3">Watchlist</h2>
        {watchlist.loading && <p className="text-gray-400 text-sm">Loading...</p>}
        {watchlist.error && <p className="text-red-400 text-sm">{watchlist.error}</p>}
        {watchlist.data && (
          <div>
            <p className="text-sm text-gray-400 mb-3">
              {watchlist.data.total} tickers across{" "}
              {Object.keys(watchlist.data.sectors).length} sectors
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
              {Object.entries(watchlist.data.sectors).map(([sector, tickers]) => (
                <div
                  key={sector}
                  className="border border-gray-700 rounded p-3 bg-gray-900"
                >
                  <h3 className="text-sm font-medium mb-2">{sector}</h3>
                  <p className="text-xs text-gray-400">
                    {tickers.length} tickers
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
