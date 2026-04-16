import type { Book, BookListResponse, BookStats, RagAnswer } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000/api";

async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers || {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `Request failed: ${response.status}`);
  }

  return (await response.json()) as T;
}

export function getBooks() {
  return apiFetch<BookListResponse>("/api/books/");
}

export async function getAllBooks() {
  let nextPath: string | null = "/api/books/";
  const aggregated: Book[] = [];

  while (nextPath) {
    const currentPath = nextPath;
    const page: BookListResponse = await apiFetch<BookListResponse>(currentPath);
    aggregated.push(...(page.results || []));

    if (!page.next) {
      nextPath = null;
      continue;
    }

    if (page.next.startsWith(API_BASE)) {
      nextPath = page.next.slice(API_BASE.length);
    } else if (page.next.startsWith("/")) {
      nextPath = page.next;
    } else {
      try {
        const parsed = new URL(page.next);
        nextPath = `${parsed.pathname}${parsed.search}`.replace(/^\/api/, "");
      } catch {
        nextPath = null;
      }
    }
  }

  return aggregated;
}

export function getBook(id: string | number) {
  return apiFetch<Book>(`/api/books/${id}/`);
}

export function getStats() {
  return apiFetch<BookStats>("/api/books/stats/");
}

export function getRecommendations(id: string | number) {
  return apiFetch<{ book_id: number; recommendations: Book[] }>(`/api/books/${id}/recommendations/`);
}

export function scrapeBooks(
  pages = 2,
  maxBooks = 40,
  options?: {
    processAI?: boolean;
    aiLimit?: number;
  },
) {
  return apiFetch<{
    detail: string;
    created: number;
    updated: number;
    total_processed: number;
    ai_processed_count: number;
    indexed_chunks: number;
  }>("/api/books/scrape/", {
    method: "POST",
    body: JSON.stringify({
      pages,
      max_books: maxBooks,
      process_ai: options?.processAI ?? true,
      ai_limit: options?.aiLimit ?? 120,
    }),
  });
}

export function askQuestion(payload: { question: string; book_id?: number | null }) {
  return apiFetch<RagAnswer>("/api/rag/ask/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
