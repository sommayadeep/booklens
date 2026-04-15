"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { ArrowUpRight, Star } from "lucide-react";

import { GlassPanel } from "@/components/glass-panel";
import { getBook, getRecommendations } from "@/lib/api";
import type { Book } from "@/types";

export default function BookDetailPage() {
  const params = useParams<{ id: string }>();
  const id = params?.id;

  const [book, setBook] = useState<Book | null>(null);
  const [recommendations, setRecommendations] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!id) return;

    async function load() {
      try {
        setLoading(true);
        const [bookRes, recRes] = await Promise.all([getBook(id), getRecommendations(id)]);
        setBook(bookRes);
        setRecommendations(recRes.recommendations || []);
        setError("");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load book details");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [id]);

  const quickMeta = useMemo(
    () => [
      { label: "Genre", value: book?.genre || "General" },
      { label: "Sentiment", value: book?.sentiment || "Neutral" },
      { label: "Rating", value: book?.rating ? `${book.rating.toFixed(1)} / 5` : "N/A" },
      { label: "Reviews", value: book?.reviews_count ?? 0 },
    ],
    [book],
  );

  if (loading) {
    return <div className="h-64 animate-pulse rounded-panel border border-black/10 bg-white/60" />;
  }

  if (error || !book) {
    return (
      <GlassPanel className="p-8 text-center">
        <p className="text-sm text-red-600">{error || "Book not found."}</p>
      </GlassPanel>
    );
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
      <GlassPanel className="glass-grid space-y-5 p-6 sm:p-7">
        <p className="text-xs uppercase tracking-[0.2em] text-muted">Book Detail</p>
        <h1 className="heading-font text-4xl leading-tight text-ink">{book.title}</h1>
        <p className="text-body">by {book.author || "Unknown"}</p>

        <div className="grid gap-3 sm:grid-cols-2">
          {quickMeta.map((item) => (
            <div key={item.label} className="rounded-2xl border border-black/10 bg-white/75 p-3 shadow-sm">
              <p className="text-xs uppercase tracking-[0.15em] text-muted">{item.label}</p>
              <p className="mt-1 text-sm font-semibold text-ink">{item.value}</p>
            </div>
          ))}
        </div>

        <div className="rounded-2xl border border-black/10 bg-white/70 p-4 shadow-sm">
          <p className="text-xs uppercase tracking-[0.15em] text-muted">Description</p>
          <p className="mt-2 text-sm leading-6 text-body">{book.description || "No description available."}</p>
        </div>

        <Link
          href={book.book_url}
          target="_blank"
          className="inline-flex items-center gap-2 rounded-full border border-black/10 bg-white/75 px-4 py-2 text-sm text-ink transition duration-300 hover:-translate-y-0.5 hover:bg-black/5"
        >
          Visit Source <ArrowUpRight className="h-4 w-4" />
        </Link>
      </GlassPanel>

      <div className="space-y-4">
        <InsightCard title="Summary" body={book.summary || "Summary unavailable."} />
        <InsightCard
          title="Genre Classification"
          body={`This book is classified as ${book.genre || "General"} based on semantic analysis of description and metadata.`}
        />
        <InsightCard
          title="Recommendations"
          body={
            recommendations.length
              ? recommendations
                  .slice(0, 4)
                  .map((item) => `${item.title} by ${item.author || "Unknown"}`)
                  .join(" • ")
              : "No similar books available yet. Ingest more books to improve recommendations."
          }
        />

        {recommendations.length > 0 && (
          <GlassPanel className="p-4">
            <p className="mb-3 text-xs uppercase tracking-[0.15em] text-muted">Related Books</p>
            <div className="space-y-2">
              {recommendations.slice(0, 4).map((rec) => (
                <Link
                  key={rec.id}
                  href={`/books/${rec.id}`}
                  className="flex items-center justify-between rounded-xl border border-black/10 bg-white/75 px-3 py-2 text-sm transition hover:bg-black/5"
                >
                  <span className="line-clamp-1 text-ink">{rec.title}</span>
                  <span className="inline-flex items-center gap-1 text-muted">
                    <Star className="h-3.5 w-3.5" />
                    {rec.rating ? rec.rating.toFixed(1) : "N/A"}
                  </span>
                </Link>
              ))}
            </div>
          </GlassPanel>
        )}
      </div>
    </div>
  );
}

function InsightCard({ title, body }: { title: string; body: string }) {
  return (
    <GlassPanel className="p-4 transition duration-300 hover:-translate-y-0.5">
      <p className="text-xs uppercase tracking-[0.15em] text-muted">{title}</p>
      <p className="mt-2 text-sm leading-6 text-body">{body}</p>
    </GlassPanel>
  );
}
