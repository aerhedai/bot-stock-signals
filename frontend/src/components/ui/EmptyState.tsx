import type { ReactNode } from "react";

interface Props {
  icon: ReactNode;
  message: string;
}

export default function EmptyState({ icon, message }: Props) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-text-muted">
      <div className="mb-3">{icon}</div>
      <p className="text-sm">{message}</p>
    </div>
  );
}
