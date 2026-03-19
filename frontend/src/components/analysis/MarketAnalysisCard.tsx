import type { MarketAnalysisResponse } from "@/lib/types";
import { formatDateShort } from "@/lib/format";

interface Props {
  title: string;
  data: MarketAnalysisResponse | null;
  loading: boolean;
  error: string | null;
}

export default function MarketAnalysisCard({ title, data, loading, error }: Props) {
  return (
    <div className="border border-border-primary rounded-xl p-5 bg-surface-card">
      <div className="flex justify-between items-center mb-3">
        <h2 className="text-sm font-semibold">{title}</h2>
        {data && (
          <span className="text-xs text-text-muted">
            {data.headline_count} headlines · {formatDateShort(data.generated_at)}
          </span>
        )}
      </div>

      {loading && (
        <div className="space-y-2">
          <div className="h-3 bg-surface-hover rounded animate-pulse w-full" />
          <div className="h-3 bg-surface-hover rounded animate-pulse w-5/6" />
          <div className="h-3 bg-surface-hover rounded animate-pulse w-4/6" />
        </div>
      )}

      {error && !loading && (
        <p className="text-sm text-text-muted italic">
          No analysis available yet — trigger one to get started.
        </p>
      )}

      {data && !loading && (
        <p className="text-sm text-text-secondary leading-relaxed">{data.analysis}</p>
      )}
    </div>
  );
}
