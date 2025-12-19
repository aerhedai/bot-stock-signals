import type { NewsArticle } from "@/lib/types";

interface Props {
  article: NewsArticle;
}

export default function NewsCard({ article }: Props) {
  const categoryColor =
    article.category === "crypto" ? "text-yellow-400" : "text-green-400";

  return (
    <div className="border border-gray-700 rounded-lg p-4 bg-gray-900">
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
          className="text-xs text-blue-400 hover:underline"
        >
          Read more
        </a>
      )}
      <div className="text-xs text-gray-500 mt-2">{article.sent_at}</div>
    </div>
  );
}
