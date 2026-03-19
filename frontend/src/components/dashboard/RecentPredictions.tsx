import Link from "next/link";
import type { StockSignal } from "@/lib/types";

interface Props {
  alerts: Record<string, StockSignal>;
}

export default function RecentPredictions({ alerts }: Props) {
  const entries = Object.values(alerts)
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
    .slice(0, 5);

  return (
    <div className="border border-border-primary rounded-xl bg-surface-card">
      <div className="flex items-center justify-between px-4 py-3 border-b border-border-subtle">
        <p className="text-xs font-medium uppercase tracking-wider text-text-muted">
          Recent Predictions
        </p>
        <Link
          href="/predictions/stocks"
          className="text-xs text-accent hover:underline"
        >
          View all &rarr;
        </Link>
      </div>
      {entries.length === 0 ? (
        <p className="px-4 py-6 text-sm text-text-muted text-center">
          No predictions yet.
        </p>
      ) : (
        <div className="divide-y divide-border-subtle">
          {entries.map((e, i) => (
            <div key={i} className="px-4 py-2.5 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium">{e.ticker}</span>
                <span className="text-xs text-text-muted">{e.method}</span>
              </div>
              <div className="flex items-center gap-3">
                <span className="text-sm text-accent">{e.score.toFixed(1)}</span>
                <span className="text-xs text-text-muted">${e.price.toFixed(2)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
