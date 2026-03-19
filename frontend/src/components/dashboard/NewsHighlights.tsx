import Link from "next/link";
import type { NewsArticle } from "@/lib/types";
import { ExternalLink } from "@/components/icons";

interface Props {
  articles: NewsArticle[];
}

export default function NewsHighlights({ articles }: Props) {
  const items = articles.slice(0, 3);

  return (
    <div className="border border-border-primary rounded-xl bg-surface-card">
      <div className="flex items-center justify-between px-4 py-3 border-b border-border-subtle">
        <p className="text-xs font-medium uppercase tracking-wider text-text-muted">
          News Highlights
        </p>
        <Link
          href="/news"
          className="text-xs text-accent hover:underline"
        >
          View all &rarr;
        </Link>
      </div>
      {items.length === 0 ? (
        <p className="px-4 py-6 text-sm text-text-muted text-center">
          No news articles yet.
        </p>
      ) : (
        <div className="divide-y divide-border-subtle">
          {items.map((article) => (
            <div key={article.id} className="px-4 py-2.5 flex items-start justify-between gap-3">
              <div className="min-w-0 flex-1">
                <p className="text-sm text-text-primary truncate">
                  {article.headline}
                </p>
                <p className="text-xs text-text-muted mt-0.5">
                  {article.source} &middot; {article.category}
                </p>
              </div>
              {article.url && (
                <a
                  href={article.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-text-muted hover:text-accent shrink-0 mt-0.5"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
