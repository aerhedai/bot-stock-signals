"use client";

import { useApi } from "@/hooks/useApi";
import { getNewsFeed, triggerNewsFetch } from "@/lib/api";
import NewsCard from "@/components/news/NewsCard";
import PageHeader from "@/components/layout/PageHeader";
import LoadingSkeleton from "@/components/ui/LoadingSkeleton";
import EmptyState from "@/components/ui/EmptyState";
import { Newspaper } from "@/components/icons";
import { useState, useMemo } from "react";
import type { NewsArticle } from "@/lib/types";

type FilterTab = "all" | "stock" | "crypto";

function StatPill({ label, value }: { label: string; value: number }) {
  return (
    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-surface-card border border-border-primary">
      <span className="text-sm font-semibold text-text-primary">{value}</span>
      <span className="text-xs text-text-muted">{label}</span>
    </div>
  );
}

function FilterTab({
  label,
  active,
  count,
  onClick,
}: {
  label: string;
  active: boolean;
  count: number;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
        active
          ? "bg-accent text-white"
          : "text-text-secondary hover:text-text-primary hover:bg-surface-hover"
      }`}
    >
      {label}
      <span
        className={`text-xs px-1.5 py-0.5 rounded-full ${
          active ? "bg-white/20 text-white" : "bg-surface-active text-text-muted"
        }`}
      >
        {count}
      </span>
    </button>
  );
}

export default function NewsPage() {
  const feed = useApi(getNewsFeed);
  const [fetching, setFetching] = useState(false);
  const [fetchMsg, setFetchMsg] = useState("");
  const [activeTab, setActiveTab] = useState<FilterTab>("all");
  const [search, setSearch] = useState("");

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

  const articles = feed.data?.articles ?? [];

  const filtered = useMemo(() => {
    let list: NewsArticle[] = articles;
    if (activeTab !== "all") {
      list = list.filter((a) => a.category === activeTab);
    }
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      list = list.filter(
        (a) =>
          a.headline.toLowerCase().includes(q) ||
          (a.ticker && a.ticker.toLowerCase().includes(q)) ||
          (a.source && a.source.toLowerCase().includes(q))
      );
    }
    return list;
  }, [articles, activeTab, search]);

  const stockCount = articles.filter((a) => a.category === "stock").length;
  const cryptoCount = articles.filter((a) => a.category === "crypto").length;
  const tickerCount = articles.filter((a) => !!a.ticker).length;

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
      {feed.error && (
        <p className="text-semantic-error text-sm">{feed.error}</p>
      )}

      {feed.data && (
        <div>
          {/* Stats row */}
          <div className="flex items-center gap-2 flex-wrap mb-5">
            <StatPill label="total" value={feed.data.total} />
            <StatPill label="stock" value={stockCount} />
            <StatPill label="crypto" value={cryptoCount} />
            {tickerCount > 0 && (
              <StatPill label="company-specific" value={tickerCount} />
            )}
          </div>

          {/* Filter tabs + search row */}
          <div className="flex items-center gap-2 flex-wrap mb-5">
            <div className="flex items-center gap-1 p-1 rounded-lg bg-surface-card border border-border-primary">
              <FilterTab
                label="All"
                active={activeTab === "all"}
                count={articles.length}
                onClick={() => setActiveTab("all")}
              />
              <FilterTab
                label="Stock"
                active={activeTab === "stock"}
                count={stockCount}
                onClick={() => setActiveTab("stock")}
              />
              <FilterTab
                label="Crypto"
                active={activeTab === "crypto"}
                count={cryptoCount}
                onClick={() => setActiveTab("crypto")}
              />
            </div>

            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search headlines, ticker, source…"
              className="flex-1 min-w-[200px] text-sm bg-surface-card border border-border-primary rounded-lg px-3 py-1.5 text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent"
            />

            {(search || activeTab !== "all") && (
              <span className="text-xs text-text-muted">
                {filtered.length} result{filtered.length !== 1 ? "s" : ""}
              </span>
            )}
          </div>

          {/* Articles grid */}
          {filtered.length === 0 ? (
            <EmptyState
              icon={<Newspaper className="w-8 h-8" />}
              message={
                search || activeTab !== "all"
                  ? "No articles match your filter."
                  : "No news articles yet."
              }
            />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
              {filtered.map((article) => (
                <NewsCard key={article.id} article={article} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
