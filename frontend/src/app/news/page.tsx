"use client";

import { useApi } from "@/hooks/useApi";
import { getNewsFeed, triggerNewsFetch } from "@/lib/api";
import NewsCard from "@/components/news/NewsCard";
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
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">News Feed</h1>
        <button
          onClick={handleFetch}
          disabled={fetching}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 text-sm"
        >
          {fetching ? "Fetching..." : "Fetch News"}
        </button>
      </div>

      {fetchMsg && (
        <p className="text-sm text-green-400 mb-4">{fetchMsg}</p>
      )}

      {feed.loading && <p className="text-gray-400 text-sm">Loading...</p>}
      {feed.error && <p className="text-red-400 text-sm">{feed.error}</p>}

      {feed.data && (
        <div>
          <p className="text-sm text-gray-400 mb-4">
            {feed.data.total} articles ({feed.data.stock_count} stock,{" "}
            {feed.data.crypto_count} crypto)
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {feed.data.articles.map((article) => (
              <NewsCard key={article.id} article={article} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
