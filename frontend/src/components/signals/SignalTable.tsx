import type { StockSignal } from "@/lib/types";

interface Props {
  alerts: Record<string, StockSignal[]>;
}

export default function SignalTable({ alerts }: Props) {
  const entries = Object.values(alerts).flat();

  if (entries.length === 0) {
    return <p className="text-gray-500 text-sm">No signals recorded yet.</p>;
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm text-left">
        <thead className="text-xs text-gray-400 uppercase border-b border-gray-700">
          <tr>
            <th className="px-4 py-2">Ticker</th>
            <th className="px-4 py-2">Method</th>
            <th className="px-4 py-2">Score</th>
            <th className="px-4 py-2">Price</th>
            <th className="px-4 py-2">Target</th>
            <th className="px-4 py-2">Time</th>
          </tr>
        </thead>
        <tbody>
          {entries.map((e, i) => (
            <tr key={i} className="border-b border-gray-800 hover:bg-gray-900">
              <td className="px-4 py-2 font-medium">{e.ticker}</td>
              <td className="px-4 py-2">{e.method}</td>
              <td className="px-4 py-2 text-blue-400">{e.score.toFixed(1)}</td>
              <td className="px-4 py-2">${e.price.toFixed(2)}</td>
              <td className="px-4 py-2">
                {e.target ? `$${e.target.toFixed(2)}` : "-"}
              </td>
              <td className="px-4 py-2 text-xs text-gray-400">{e.timestamp}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
