import type { StockSignal } from "@/lib/types";

interface Props {
  ticker: string;
  signal: StockSignal;
}

export default function SignalCard({ ticker, signal }: Props) {
  return (
    <div className="border border-gray-700 rounded-lg p-4 bg-gray-900">
      <div className="flex justify-between items-center mb-2">
        <span className="font-bold text-lg">{ticker}</span>
        <span className="text-sm text-gray-400">{signal.method}</span>
      </div>
      <div className="grid grid-cols-2 gap-2 text-sm">
        <div>
          <span className="text-gray-400">Price: </span>
          <span>${signal.price.toFixed(2)}</span>
        </div>
        {signal.target && (
          <div>
            <span className="text-gray-400">Target: </span>
            <span>${signal.target.toFixed(2)}</span>
          </div>
        )}
        <div>
          <span className="text-gray-400">Score: </span>
          <span className="text-blue-400">{signal.score.toFixed(1)}</span>
        </div>
        <div>
          <span className="text-gray-400">Time: </span>
          <span className="text-xs">{signal.timestamp}</span>
        </div>
      </div>
    </div>
  );
}
