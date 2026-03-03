import type { NewsArticle } from "@/lib/types";
import { formatDateShort } from "@/lib/format";

interface Props {
  article: NewsArticle;
}

export default function NewsCard({ article }: Props) {
  const categoryColor =
    article.category === "crypto" ? "text-semantic-warning" : "text-semantic-success";

  return (
    <div className="border border-border-primary rounded-xl p-4 bg-surface-card">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-medium text-sm leading-tight flex-1">
          {article.headline}
        </h3>
        <span className={`text-xs ml-2 uppercase ${categoryColor}`}>
          {article.category}
        </span>
      </div>
      {article.url && (
        <a
          href={article.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-accent hover:underline"
        >
          Read more
        </a>
      )}
      <div className="text-xs text-text-muted mt-2">{formatDateShort(article.sent_at)}</div>
    </div>
  );
}
