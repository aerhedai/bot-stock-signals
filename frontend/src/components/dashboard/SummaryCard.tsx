import type { ReactNode } from "react";

interface Props {
  icon: ReactNode;
  title: string;
  value: string | number;
  subtitle?: string;
}

export default function SummaryCard({ icon, title, value, subtitle }: Props) {
  return (
    <div className="border border-border-primary rounded-xl p-4 bg-surface-card">
      <div className="flex items-center gap-2.5 mb-2">
        <span className="text-text-muted">{icon}</span>
        <span className="text-xs font-medium uppercase tracking-wider text-text-muted">
          {title}
        </span>
      </div>
      <p className="text-2xl font-semibold text-text-primary">{value}</p>
      {subtitle && (
        <p className="text-xs text-text-muted mt-1">{subtitle}</p>
      )}
    </div>
  );
}
