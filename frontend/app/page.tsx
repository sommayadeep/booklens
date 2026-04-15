"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { Search } from "lucide-react";

import { BookCard } from "@/components/book-card";
import { GlassPanel } from "@/components/glass-panel";
import { StatsCard } from "@/components/stats-card";
import { getAllBooks, getStats, scrapeBooks } from "@/lib/api";
import type { Book, BookStats } from "@/types";

const defaultStats: BookStats = {
  total_books: 0,
  ai_processed: 0,
  text_chunks: 0,
  genres: 0,
  qa_sessions: 0,
};

export default function DashboardPage() {
  const BOOKS_PER_PAGE = 12;
  const AUTO_SCRAPE_PAGES = 50;
  const AUTO_SCRAPE_MAX_BOOKS = 1000;
  const [books, setBooks] = useState<Book[]>([]);
  const [stats, setStats] = useState<BookStats>(defaultStats);
  const [loading, setLoading] = useState(true);
  const [scraping, setScraping] = useState(false);
  const [query, setQuery] = useState("");
  const [activeGenre, setActiveGenre] = useState("All");
  const [currentPage, setCurrentPage] = useState(1);
  const [error, setError] = useState("");

  async function loadDashboard() {
    try {
      setLoading(true);
      const [booksRes, statsRes] = await Promise.all([getAllBooks(), getStats()]);
      setBooks(booksRes || []);
      setStats(statsRes);
      setError("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load dashboard data.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadDashboard();
  }, []);

  const genres = useMemo(() => {
    const set = new Set<string>();
    for (const book of books) {
      if (book.genre) {
        set.add(book.genre);
      }
    }
    return ["All", ...Array.from(set).sort()];
  }, [books]);

  const filteredBooks = useMemo(() => {
    const text = query.trim().toLowerCase();
    return books.filter((book) => {
      const matchesGenre = activeGenre === "All" || book.genre === activeGenre;
      if (!matchesGenre) return false;
      if (!text) return true;
      const corpus = `${book.title} ${book.author} ${book.description}`.toLowerCase();
      return corpus.includes(text);
    });
  }, [books, query, activeGenre]);

  useEffect(() => {
    setCurrentPage(1);
  }, [query, activeGenre]);

  const totalPages = Math.max(1, Math.ceil(filteredBooks.length / BOOKS_PER_PAGE));
  const paginatedBooks = useMemo(() => {
    const start = (currentPage - 1) * BOOKS_PER_PAGE;
    return filteredBooks.slice(start, start + BOOKS_PER_PAGE);
  }, [filteredBooks, currentPage]);

  useEffect(() => {
    if (currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [currentPage, totalPages]);

  async function handleScrape() {
    try {
      setScraping(true);
      await scrapeBooks(AUTO_SCRAPE_PAGES, AUTO_SCRAPE_MAX_BOOKS, { processAI: false, aiLimit: 0 });
      await loadDashboard();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scraping failed.");
    } finally {
      setScraping(false);
    }
  }

  return (
    <div className="space-y-7 pb-10">
      <GlassPanel className="glass-grid animate-fadeUp overflow-hidden p-6 sm:p-8">
        <div className="pointer-events-none absolute -left-16 -top-16 h-44 w-44 rounded-full bg-clay/30 blur-3xl" />
        <div className="pointer-events-none absolute -right-16 bottom-0 h-52 w-52 rounded-full bg-accent/20 blur-3xl" />
        <div className="grid items-center gap-5 md:grid-cols-2">
          <div>
            <p className="mb-2 text-xs uppercase tracking-[0.25em] text-muted">AI SaaS Platform</p>
            <h1 className="heading-font text-4xl leading-tight text-ink sm:text-5xl">
              Document Intelligence Platform
            </h1>
            <p className="mt-4 max-w-xl text-sm text-body sm:text-base">
              AI-powered book analysis with scraping automation, insight generation, and contextual RAG-based Q&A.
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <button className="primary-btn" onClick={handleScrape} disabled={scraping}>
                {scraping ? "Scraping..." : "Scrape Books"}
              </button>
              <Link href="/ask" className="secondary-btn">
                Ask AI
              </Link>
            </div>
          </div>

          <GlassPanel className="ml-auto w-full max-w-md border-white/70 bg-white/65 p-5 shadow-float">
            <p className="text-xs uppercase tracking-[0.2em] text-muted">Pipeline Health</p>
            <div className="mt-4 space-y-3 text-sm">
              <Row label="Books Indexed" value={stats.total_books} />
              <Row label="AI Processed" value={stats.ai_processed} />
              <Row label="Chunked Segments" value={stats.text_chunks} />
              <Row label="RAG Sessions" value={stats.qa_sessions} />
            </div>
          </GlassPanel>
        </div>
      </GlassPanel>

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <StatsCard label="Total Books" value={stats.total_books} />
        <StatsCard label="AI Processed" value={stats.ai_processed} />
        <StatsCard label="Text Chunks" value={stats.text_chunks} />
        <StatsCard label="Genres" value={stats.genres} />
        <StatsCard label="Q&A Sessions" value={stats.qa_sessions} />
      </section>

      <GlassPanel className="space-y-5 p-5 sm:p-6">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="relative w-full md:max-w-md">
            <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="glass-input pl-9"
              placeholder="Search books, authors, or topics"
            />
          </div>

          <div className="flex flex-wrap items-center gap-2">
            {genres.map((genre) => (
              <button
                key={genre}
                onClick={() => setActiveGenre(genre)}
                className={`rounded-full px-4 py-2 text-xs font-medium transition duration-300 ${
                  activeGenre === genre
                    ? "bg-black text-white shadow-[0_8px_18px_rgba(0,0,0,0.18)]"
                    : "border border-black/10 bg-white/70 text-ink hover:-translate-y-0.5 hover:bg-black/5"
                }`}
              >
                {genre}
              </button>
            ))}
          </div>
        </div>

        {error && <p className="text-sm text-red-600">{error}</p>}

        {loading ? (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="h-72 animate-pulse rounded-panel border border-black/10 bg-white/70" />
            ))}
          </div>
        ) : filteredBooks.length === 0 ? (
          <div className="rounded-2xl border border-dashed border-black/15 p-8 text-center">
            <p className="text-sm text-muted">No books found. Click "Scrape Books" to ingest data.</p>
          </div>
        ) : (
          <>
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
              {paginatedBooks.map((book) => (
                <BookCard key={book.id} book={book} />
              ))}
            </div>

            <div className="mt-6 flex flex-wrap items-center justify-center gap-2">
              <button
                className="secondary-btn px-4 py-2 disabled:opacity-50"
                disabled={currentPage === 1}
                onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
              >
                Previous
              </button>

              {buildPaginationPages(totalPages, currentPage).map((page, idx) => {
                if (page === "...") {
                  return (
                    <span key={`dots-${idx}`} className="px-1 text-sm text-muted">
                      ...
                    </span>
                  );
                }

                const active = page === currentPage;
                return (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`h-10 min-w-10 rounded-full px-3 text-sm transition ${
                      active
                        ? "bg-black text-white shadow-[0_8px_16px_rgba(0,0,0,0.2)]"
                        : "border border-black/10 bg-white/75 text-ink hover:bg-black/5"
                    }`}
                  >
                    {page}
                  </button>
                );
              })}

              <button
                className="secondary-btn px-4 py-2 disabled:opacity-50"
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
              >
                Next
              </button>
            </div>
          </>
        )}
      </GlassPanel>
    </div>
  );
}

function buildPaginationPages(totalPages: number, currentPage: number): Array<number | "..."> {
  if (totalPages <= 9) {
    return Array.from({ length: totalPages }, (_, i) => i + 1);
  }

  const pages: Array<number | "..."> = [1];
  const start = Math.max(2, currentPage - 2);
  const end = Math.min(totalPages - 1, currentPage + 2);

  if (start > 2) {
    pages.push("...");
  }

  for (let p = start; p <= end; p += 1) {
    pages.push(p);
  }

  if (end < totalPages - 1) {
    pages.push("...");
  }

  pages.push(totalPages);
  return pages;
}

function Row({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex items-center justify-between rounded-xl border border-black/10 bg-white/75 px-3 py-2 shadow-sm">
      <span className="text-body">{label}</span>
      <span className="font-semibold text-ink">{value}</span>
    </div>
  );
}
