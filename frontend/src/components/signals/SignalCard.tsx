import type { StockSignal } from "@/lib/types";
import { formatDateShort } from "@/lib/format";

interface Props {
  ticker: string;
  signal: StockSignal;
}

export default function SignalCard({ ticker, signal }: Props) {
  return (
    <div className="border border-border-primary rounded-xl p-4 bg-surface-card">
      <div className="flex justify-between items-center mb-2">
        <span className="font-bold text-lg">{ticker}</span>
        <span className="text-sm text-text-secondary">{signal.method}</span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div>
          <span className="text-text-secondary">Price: </span>
          <span>${signal.price.toFixed(2)}</span>
        </div>
        {signal.target && (
          <div>
            <span className="text-text-secondary">Target: </span>
            <span>${signal.target.toFixed(2)}</span>
          </div>
        )}
        <div>
          <span className="text-text-secondary">Score: </span>
          <span className="text-accent">{signal.score.toFixed(1)}</span>
        </div>
        <div>
          <span className="text-text-secondary">Time: </span>
          <span className="text-xs">{formatDateShort(signal.timestamp)}</span>
        </div>
      </div>
    </div>
  );
}
