"use client";

import { useState, useEffect } from "react";
import {
  ResponsiveContainer, ComposedChart, Line, ReferenceLine, ReferenceDot,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from "recharts";
import type { StockChartData } from "@/lib/types";
import { getStockChart } from "@/lib/api";

interface Props {
  ticker: string;
  targetPrice: number | null;
  entryPrice: number;
  signalTimestamp: string;
  timeHorizon: string;
}

function formatPrice(v: number) {
  return `$${v.toFixed(2)}`;
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr);
  return d.toLocaleDateString("en-GB", { day: "numeric", month: "short" });
}

export default function StockDetailChart({ ticker, targetPrice, entryPrice, signalTimestamp, timeHorizon }: Props) {
  const [chart, setChart] = useState<StockChartData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    getStockChart(ticker)
      .then(setChart)
      .catch(() => setError("Failed to load chart data"))
      .finally(() => setLoading(false));
  }, [ticker]);

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
  const upsidePct = targetPrice ? ((targetPrice - latestPrice) / latestPrice) * 100 : null;
  const signalDate = signalTimestamp.slice(0, 10);

  // Domain padding for Y axis
  const prices = chart.data.map(d => d.price);
  const allValues = [...prices, ...(targetPrice ? [targetPrice] : [])];
  const minY = Math.min(...allValues) * 0.97;
  const maxY = Math.max(...allValues) * 1.03;

  return (
    <div className="mt-4 border-t border-border-subtle pt-4">
      {/* Stats row */}
      <div className="grid grid-cols-3 gap-2 mb-4 text-center">
        <div className="bg-surface-root rounded-lg px-2 py-2">
          <p className="text-[10px] text-text-muted mb-0.5">Current Price</p>
          <p className="text-sm font-semibold text-text-primary">${latestPrice.toFixed(2)}</p>
        </div>
        {targetPrice && (
          <div className="bg-surface-root rounded-lg px-2 py-2">
            <p className="text-[10px] text-text-muted mb-0.5">Target</p>
            <p className="text-sm font-semibold text-semantic-success">${targetPrice.toFixed(2)}</p>
          </div>
        )}
        {upsidePct !== null && (
          <div className="bg-surface-root rounded-lg px-2 py-2">
            <p className="text-[10px] text-text-muted mb-0.5">Upside</p>
            <p className={`text-sm font-semibold ${upsidePct >= 0 ? "text-semantic-success" : "text-semantic-error"}`}>
              {upsidePct >= 0 ? "+" : ""}{upsidePct.toFixed(1)}%
            </p>
          </div>
        )}
      </div>

      {/* Time horizon pill */}
      <div className="flex items-center gap-2 mb-3">
        <span className="text-[10px] uppercase tracking-wider text-text-muted">Horizon</span>
        <span className="text-xs bg-accent/10 text-accent px-2 py-0.5 rounded-full">{timeHorizon}</span>
      </div>

      {/* Chart */}
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
              tickFormatter={formatPrice}
              tick={{ fill: "#71717a", fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              width={55}
            />
            <Tooltip
              contentStyle={{ background: "#18181b", border: "1px solid #27272a", borderRadius: 8, fontSize: 12 }}
              labelStyle={{ color: "#a1a1aa" }}
              itemStyle={{ color: "#fafafa" }}
              formatter={(v) => [`$${Number(v).toFixed(2)}`]}
              labelFormatter={(label) => formatDate(String(label))}
            />
            <Legend
              iconType="plainline"
              iconSize={12}
              wrapperStyle={{ fontSize: 10, color: "#71717a", paddingTop: 4 }}
            />

            {/* Target price reference line */}
            {targetPrice && (
              <ReferenceLine
                y={targetPrice}
                stroke="#22c55e"
                strokeDasharray="5 3"
                strokeWidth={1.5}
                label={{ value: `Target $${targetPrice.toFixed(2)}`, fill: "#22c55e", fontSize: 9, position: "insideTopRight" }}
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

            <Line
              type="monotone"
              dataKey="price"
              stroke="#fafafa"
              strokeWidth={1.5}
              dot={false}
              name="Price"
            />
            <Line
              type="monotone"
              dataKey="ema20"
              stroke="#3b82f6"
              strokeWidth={1.5}
              dot={false}
              name="EMA(20)"
              strokeDasharray="4 2"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      {/* Progress to target bar */}
      {targetPrice && (
        <div className="mt-3">
          <div className="flex justify-between text-[10px] text-text-muted mb-1">
            <span>Entry ${entryPrice.toFixed(2)}</span>
            <span>Target ${targetPrice.toFixed(2)}</span>
          </div>
          <div className="h-1.5 bg-surface-active rounded-full overflow-hidden">
            <div
              className="h-full bg-semantic-success rounded-full transition-all"
              style={{
                width: `${Math.min(100, Math.max(0, ((latestPrice - entryPrice) / (targetPrice - entryPrice)) * 100))}%`
              }}
            />
          </div>
          <p className="text-[10px] text-text-muted mt-1 text-right">
            {Math.min(100, Math.max(0, ((latestPrice - entryPrice) / (targetPrice - entryPrice)) * 100)).toFixed(0)}% of the way to target
          </p>
        </div>
      )}
    </div>
  );
}
