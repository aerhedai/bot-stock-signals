interface Props {
  status: "running" | "stopped" | "error";
}

const styles: Record<Props["status"], string> = {
  running: "bg-semantic-success/15 text-semantic-success",
  stopped: "bg-surface-hover text-text-muted",
  error: "bg-semantic-error/15 text-semantic-error",
};

const labels: Record<Props["status"], string> = {
  running: "Running",
  stopped: "Stopped",
  error: "Error",
};

export default function StatusBadge({ status }: Props) {
  return (
    <span className={`inline-flex items-center text-xs px-2 py-0.5 rounded-full ${styles[status]}`}>
      {labels[status]}
    </span>
  );
}
