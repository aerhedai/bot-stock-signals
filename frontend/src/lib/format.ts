/**
 * Format a date string into a human-readable format.
 * Accepts ISO strings, Unix timestamps, or any Date-parseable string.
 */
export function formatDate(value: string | number | null | undefined): string {
  if (!value) return "Never";

  const date = new Date(value);
  if (isNaN(date.getTime())) return String(value);

  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  });
}

/**
 * Format a date string into a short relative or compact format.
 * Shows "2m ago", "3h ago", "Yesterday", or "Feb 11" for older dates.
 */
export function formatDateShort(value: string | number | null | undefined): string {
  if (!value) return "Never";

  const date = new Date(value);
  if (isNaN(date.getTime())) return String(value);

  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  const diffHr = Math.floor(diffMs / 3600000);

  if (diffMin < 1) return "Just now";
  if (diffMin < 60) return `${diffMin}m ago`;
  if (diffHr < 24) return `${diffHr}h ago`;
  if (diffHr < 48) return "Yesterday";

  return date.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
  });
}
