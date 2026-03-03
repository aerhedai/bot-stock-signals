"use client";

import { useApi } from "@/hooks/useApi";
import { getNewsFeed, triggerNewsFetch } from "@/lib/api";
import NewsCard from "@/components/news/NewsCard";
import PageHeader from "@/components/layout/PageHeader";
import LoadingSkeleton from "@/components/ui/LoadingSkeleton";
import EmptyState from "@/components/ui/EmptyState";
import { Newspaper } from "@/components/icons";
import { useState } from "react";

export default function NewsPage() {
  const feed = useApi(getNewsFeed);
  const [fetching, setFetching] = useState(false);
  const [fetchMsg, setFetchMsg] = useState("");

  const handleFetch = async () => {
    setFetching(true);
    setFetchMsg("");
    try {
      const result = await triggerNewsFetch();
      setFetchMsg(result.message);
      feed.refetch();
    } catch {
      setFetchMsg("Fetch failed.");
    } finally {
      setFetching(false);
    }
  };

  return (
    <div>
      <PageHeader
        title="News Feed"
        action={
          <button
            onClick={handleFetch}
            disabled={fetching}
            className="px-3 py-1.5 bg-accent text-white rounded-lg hover:bg-accent-hover disabled:opacity-50 text-sm transition-colors"
          >
            {fetching ? "Fetching..." : "Fetch News"}
          </button>
        }
      />

      {fetchMsg && (
        <p className="text-sm text-semantic-success mb-4">{fetchMsg}</p>
      )}

      {feed.loading && <LoadingSkeleton lines={6} />}
      {feed.error && <p className="text-semantic-error text-sm">{feed.error}</p>}

      {feed.data && (
        <div>
          <p className="text-sm text-text-secondary mb-4">
            {feed.data.total} articles ({feed.data.stock_count} stock,{" "}
            {feed.data.crypto_count} crypto)
          </p>
          {feed.data.articles.length === 0 ? (
            <EmptyState
              icon={<Newspaper className="w-8 h-8" />}
              message="No news articles yet."
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {feed.data.articles.map((article) => (
                <NewsCard key={article.id} article={article} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
