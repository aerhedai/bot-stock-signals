interface Props {
  lines?: number;
  className?: string;
}

export default function LoadingSkeleton({ lines = 3, className = "" }: Props) {
  return (
    <div className={`space-y-3 ${className}`}>
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-4 rounded bg-surface-hover animate-pulse"
          style={{ width: `${100 - i * 15}%` }}
        />
      ))}
    </div>
  );
}
