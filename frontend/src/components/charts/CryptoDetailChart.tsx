"use client";

import { useState, useEffect } from "react";
import {
  ResponsiveContainer, ComposedChart, Line, ReferenceLine, ReferenceDot,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from "recharts";
import type { CryptoChartData } from "@/lib/types";
import { getCryptoChart } from "@/lib/api";

interface Props {
  symbol: string;
  fairValue: number | null;
  entryPrice: number;
  signalTimestamp: string;
  rsi: number | null;
  change24h: number | null;
  change7d: number | null;
}

function formatCryptoPrice(v: number) {
  if (v >= 1000) return `$${v.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
  if (v >= 1) return `$${v.toFixed(2)}`;
  return `$${v.toFixed(6)}`;
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
}

function RsiGauge({ rsi }: { rsi: number }) {
  const pct = Math.min(100, Math.max(0, rsi));
  const colour = rsi <= 30 ? "#22c55e" : rsi >= 70 ? "#ef4444" : "#3b82f6";
  const label = rsi <= 30 ? "Oversold" : rsi >= 70 ? "Overbought" : "Neutral";
  return (
    <div>
      <div className="flex justify-between text-[10px] text-text-muted mb-1">
        <span>RSI — {label}</span>
        <span style={{ color: colour }}>{rsi.toFixed(1)}</span>
      </div>
      <div className="relative h-1.5 bg-surface-active rounded-full overflow-hidden">
        {/* Zone markers */}
        <div className="absolute top-0 left-[30%] w-px h-full bg-surface-hover" />
        <div className="absolute top-0 left-[70%] w-px h-full bg-surface-hover" />
        <div className="absolute top-0 left-0 h-full rounded-full transition-all" style={{ width: `${pct}%`, background: colour }} />
      </div>
      <div className="flex justify-between text-[9px] text-text-muted mt-0.5">
        <span>0</span><span>30</span><span>70</span><span>100</span>
      </div>
    </div>
  );
}

export default function CryptoDetailChart({ symbol, fairValue, entryPrice, signalTimestamp, rsi, change24h, change7d }: Props) {
  const [chart, setChart] = useState<CryptoChartData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getCryptoChart(symbol)
      .then(setChart)
      .catch(() => setError("Failed to load chart data"))
      .finally(() => setLoading(false));
  }, [symbol]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-40 text-text-muted text-xs">
        Loading chart…
      </div>
    );
  }

  if (error || !chart) {
    return (
      <div className="flex items-center justify-center h-40 text-semantic-error text-xs">
        {error ?? "No chart data available"}
      </div>
    );
  }

  const latestPrice = chart.data.at(-1)?.price ?? entryPrice;
  const discountPct = fairValue ? ((fairValue - latestPrice) / fairValue) * 100 : null;
  const signalDate = signalTimestamp.slice(0, 10);

  // Y axis domain based on price + bands
  const prices = chart.data.map(d => d.price);
  const uppers = chart.data.map(d => d.bb_upper ?? d.price);
  const lowers = chart.data.map(d => d.bb_lower ?? d.price);
  const allVals = [...prices, ...uppers, ...lowers, ...(fairValue ? [fairValue] : [])].filter(Boolean);
  const minY = Math.min(...allVals) * 0.97;
  const maxY = Math.max(...allVals) * 1.03;

  return (
    <div className="mt-4 border-t border-border-subtle pt-4">
      {/* Stats row */}
      <div className="grid grid-cols-3 gap-2 mb-4 text-center">
        <div className="bg-surface-root rounded-lg px-2 py-2">
          <p className="text-[10px] text-text-muted mb-0.5">Current Price</p>
          <p className="text-sm font-semibold text-text-primary">{formatCryptoPrice(latestPrice)}</p>
        </div>
        {fairValue && (
          <div className="bg-surface-root rounded-lg px-2 py-2">
            <p className="text-[10px] text-text-muted mb-0.5">Fair Value</p>
            <p className="text-sm font-semibold text-semantic-success">{formatCryptoPrice(fairValue)}</p>
          </div>
        )}
        {discountPct !== null && (
          <div className="bg-surface-root rounded-lg px-2 py-2">
            <p className="text-[10px] text-text-muted mb-0.5">Discount</p>
            <p className="text-sm font-semibold text-semantic-warning">{discountPct.toFixed(1)}%</p>
          </div>
        )}
      </div>

      {/* 24h / 7d chips */}
      <div className="flex items-center gap-3 mb-3">
        {change24h !== null && (
          <div className="text-xs">
            <span className="text-text-muted">24h </span>
            <span className={change24h >= 0 ? "text-semantic-success font-medium" : "text-semantic-error font-medium"}>
              {change24h >= 0 ? "+" : ""}{change24h.toFixed(2)}%
            </span>
          </div>
        )}
        {change7d !== null && (
          <div className="text-xs">
            <span className="text-text-muted">7d </span>
            <span className={change7d >= 0 ? "text-semantic-success font-medium" : "text-semantic-error font-medium"}>
              {change7d >= 0 ? "+" : ""}{change7d.toFixed(2)}%
            </span>
          </div>
        )}
      </div>

      {/* Price chart with Bollinger Bands */}
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={chart.data} margin={{ top: 4, right: 8, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" vertical={false} />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              tick={{ fill: "#71717a", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              interval="preserveStartEnd"
            />
            <YAxis
              domain={[minY, maxY]}
              tickFormatter={formatCryptoPrice}
              tick={{ fill: "#71717a", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              width={60}
            />
            <Tooltip
              contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: 8, fontSize: 12 }}
              labelStyle={{ color: "#a1a1aa" }}
              itemStyle={{ color: "#fafafa" }}
              formatter={(v) => [formatCryptoPrice(Number(v))]}
              labelFormatter={(label) => formatDate(String(label))}
            />
            <Legend
              iconType="plainline"
              iconSize={12}
              wrapperStyle={{ fontSize: 10, color: "#71717a", paddingTop: 4 }}
            />

            {/* Fair value reference line */}
            {fairValue && (
              <ReferenceLine
                y={fairValue}
                stroke="#22c55e"
                strokeDasharray="5 3"
                strokeWidth={1.5}
                label={{ value: `Fair ${formatCryptoPrice(fairValue)}`, fill: "#22c55e", fontSize: 9, position: "insideTopRight" }}
              />
            )}

            {/* Signal entry dot */}
            <ReferenceDot
              x={signalDate}
              y={entryPrice}
              r={4}
              fill="#3b82f6"
              stroke="#09090b"
              strokeWidth={2}
              label={{ value: "Entry", fill: "#3b82f6", fontSize: 9, position: "top" }}
            />

            {/* Bollinger upper/lower shading via lines */}
            <Line type="monotone" dataKey="bb_upper" stroke="#3b82f6" strokeWidth={1} dot={false} name="BB Upper" strokeDasharray="3 3" strokeOpacity={0.5} />
            <Line type="monotone" dataKey="bb_mid" stroke="#3b82f6" strokeWidth={1} dot={false} name="BB Mid" strokeOpacity={0.4} />
            <Line type="monotone" dataKey="bb_lower" stroke="#3b82f6" strokeWidth={1} dot={false} name="BB Lower" strokeDasharray="3 3" strokeOpacity={0.5} />
            <Line type="monotone" dataKey="price" stroke="#fafafa" strokeWidth={1.5} dot={false} name="Price" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* RSI gauge */}
      {rsi !== null && (
        <div className="mt-4">
          <RsiGauge rsi={rsi} />
        </div>
      )}
    </div>
  );
}
