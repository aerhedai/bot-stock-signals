"use client";

import { useState } from "react";
import { useApi } from "@/hooks/useApi";
import { getStockAnalysis, getCryptoAnalysis, triggerAnalysis } from "@/lib/api";
import PageHeader from "@/components/layout/PageHeader";
import MarketAnalysisCard from "@/components/analysis/MarketAnalysisCard";
import { RefreshCw } from "@/components/icons";

export default function AnalysisPage() {
  const stocks = useApi(getStockAnalysis);
  const crypto = useApi(getCryptoAnalysis);
  const [triggering, setTriggering] = useState(false);
  const [triggerMsg, setTriggerMsg] = useState<string | null>(null);

  async function handleTrigger() {
    setTriggering(true);
    setTriggerMsg(null);
    try {
      const result = await triggerAnalysis();
      setTriggerMsg(result.message);
      stocks.refetch();
      crypto.refetch();
    } catch {
      setTriggerMsg("Failed to trigger analysis. Check backend logs.");
    } finally {
      setTriggering(false);
    }
  }

  return (
    <div>
      <PageHeader title="AI Market Analysis" />

      <div className="flex items-center justify-between mb-6">
        <p className="text-sm text-text-muted">
          AI-generated summaries of current market conditions based on recent news.
        </p>
        <button
          onClick={handleTrigger}
          disabled={triggering}
          className="flex items-center gap-2 text-sm px-3 py-1.5 rounded-lg border border-border-primary bg-surface-card hover:bg-surface-hover transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${triggering ? "animate-spin" : ""}`} />
          {triggering ? "Generating..." : "Refresh Analysis"}
        </button>
      </div>

      {triggerMsg && (
        <div className="mb-4 text-xs text-text-muted border border-border-subtle rounded-lg px-3 py-2 bg-surface-card">
          {triggerMsg}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <MarketAnalysisCard
          title="Stock Market"
          data={stocks.data}
          loading={stocks.loading}
          error={stocks.error}
        />
        <MarketAnalysisCard
          title="Crypto Market"
          data={crypto.data}
          loading={crypto.loading}
          error={crypto.error}
        />
      </div>
    </div>
  );
}
