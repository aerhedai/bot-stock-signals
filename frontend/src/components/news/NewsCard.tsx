import type { NewsArticle } from "@/lib/types";
import { formatDateShort } from "@/lib/format";

interface Props {
  article: NewsArticle;
}

export default function NewsCard({ article }: Props) {
  const isStock = article.category === "stock";
  const isCrypto = article.category === "crypto";

  const categoryStyle = isCrypto
    ? "bg-semantic-warning/10 text-semantic-warning"
    : isStock
    ? "bg-semantic-success/10 text-semantic-success"
    : "bg-surface-active text-text-secondary";

  const categoryLabel = isCrypto ? "Crypto" : isStock ? "Stock" : article.category;

  return (
    <div className="border border-border-primary rounded-xl bg-surface-card hover:bg-surface-hover transition-colors overflow-hidden group">
      <div className="p-4">
        {/* Top row: category badge + ticker + date */}
        <div className="flex items-center gap-2 mb-3">
          <span className={`text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded ${categoryStyle}`}>
            {categoryLabel}
          </span>
          {article.ticker && (
            <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-accent/10 text-accent">
              {article.ticker}
            </span>
          )}
          <span className="text-xs text-text-muted ml-auto">{formatDateShort(article.sent_at)}</span>
        </div>

        {/* Headline */}
        <p className="text-sm font-medium text-text-primary leading-snug mb-3 line-clamp-3">
          {article.headline}
        </p>

        {/* Footer: source + read more */}
        <div className="flex items-center justify-between">
          {article.source ? (
            <span className="text-xs text-text-muted truncate max-w-[60%]">{article.source}</span>
          ) : (
            <span />
          )}
          {article.url && (
            <a
              href={article.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-accent hover:underline flex-shrink-0"
              onClick={(e) => e.stopPropagation()}
            >
              Read more →
            </a>
          )}
        </div>
      </div>
    </div>
  );
}
