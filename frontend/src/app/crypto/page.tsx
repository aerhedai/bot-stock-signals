"use client";

import { useApi } from "@/hooks/useApi";
import { getCryptoSignals, getCryptoWatchlist, triggerCryptoScan } from "@/lib/api";
import { useState } from "react";

export default function CryptoPage() {
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
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Crypto Signals</h1>
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
        <h2 className="text-lg font-semibold mb-3">Alert History</h2>
        {signals.loading && <p className="text-gray-400 text-sm">Loading...</p>}
        {signals.error && <p className="text-red-400 text-sm">{signals.error}</p>}
        {signals.data && (
          <div>
            <p className="text-sm text-gray-400 mb-2">
              {signals.data.total_alerts} total alerts
            </p>
            {Object.keys(signals.data.alerts).length === 0 ? (
              <p className="text-gray-500 text-sm">No alerts recorded yet.</p>
            ) : (
              <div className="space-y-2">
                {Object.entries(signals.data.alerts).map(([symbol, ts]) => (
                  <div
                    key={symbol}
                    className="flex justify-between items-center border border-gray-700 rounded p-3 bg-gray-900"
                  >
                    <span className="font-medium">{symbol}</span>
                    <span className="text-xs text-gray-400">{ts}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </section>

      <section>
        <h2 className="text-lg font-semibold mb-3">Watchlist</h2>
        {watchlist.loading && <p className="text-gray-400 text-sm">Loading...</p>}
        {watchlist.error && <p className="text-red-400 text-sm">{watchlist.error}</p>}
        {watchlist.data && (
          <div>
            <p className="text-sm text-gray-400 mb-3">
              {watchlist.data.total} cryptocurrencies
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {Object.entries(watchlist.data.categories).map(
                ([category, symbols]) => (
                  <div
                    key={category}
                    className="border border-gray-700 rounded p-3 bg-gray-900"
                  >
                    <h3 className="text-sm font-medium mb-2">{category}</h3>
                    <p className="text-xs text-gray-400">
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
