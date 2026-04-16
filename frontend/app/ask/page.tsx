"use client";

import { FormEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { isLoggedIn } from "@/lib/auth";
import Link from "next/link";

import { GlassPanel } from "@/components/glass-panel";
import { LoadingDots } from "@/components/loading-dots";
import { askQuestion, getAllBooks } from "@/lib/api";
import type { Book, SourceCitation } from "@/types";

type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: SourceCitation[];
};

export default function AskPage() {
  const router = useRouter();
  useEffect(() => {
    if (typeof window !== "undefined" && !isLoggedIn()) {
      router.replace("/login");
    }
  }, []);
  const [books, setBooks] = useState<Book[]>([]);
  const [selectedBookId, setSelectedBookId] = useState<string>("");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "intro",
      role: "assistant",
      content:
        "Ask about summaries, genres, or detailed reasoning from indexed books. I will answer with citation badges.",
    },
  ]);

  useEffect(() => {
    async function loadBooks() {
      try {
        const data = await getAllBooks();
        setBooks(data || []);
      } catch {
        setBooks([]);
      }
    }
    loadBooks();
  }, []);

  async function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || loading) return;

    const userMsg: ChatMessage = {
      id: `u-${Date.now()}`,
      role: "user",
      content: trimmed,
    };
    setMessages((prev) => [...prev, userMsg]);
    setQuestion("");
    setLoading(true);

    try {
      const response = await askQuestion({
        question: trimmed,
        book_id: selectedBookId ? Number(selectedBookId) : null,
      });

      const aiMsg: ChatMessage = {
        id: `a-${response.id}`,
        role: "assistant",
        content: response.answer,
        sources: response.sources,
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (error) {
      const fallback: ChatMessage = {
        id: `a-${Date.now()}`,
        role: "assistant",
        content: error instanceof Error ? error.message : "Something went wrong while generating an answer.",
      };
      setMessages((prev) => [...prev, fallback]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-5">
      <div className="text-center">
        <p className="text-xs uppercase tracking-[0.22em] text-muted">RAG Copilot</p>
        <h1 className="heading-font mt-1 text-4xl text-ink">Ask AI About Your Books</h1>
        <p className="mt-2 text-sm text-body">Question answering over chunked book context with source citations.</p>
      </div>

      <GlassPanel className="glass-grid p-4 sm:p-6">
        <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <label className="text-xs uppercase tracking-[0.16em] text-muted">Scope</label>
          <select
            className="glass-input w-full sm:w-72"
            value={selectedBookId}
            onChange={(e) => setSelectedBookId(e.target.value)}
          >
            <option value="">All Indexed Books</option>
            {books.map((book) => (
              <option key={book.id} value={book.id}>
                {book.title}
              </option>
            ))}
          </select>
        </div>

        <div className="max-h-[56vh] space-y-3 overflow-y-auto rounded-2xl border border-black/10 bg-white/70 p-3 shadow-inner sm:p-4">
          {messages.map((msg) => (
            <div key={msg.id} className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}>
              <div
                className={`max-w-[90%] rounded-2xl px-4 py-3 text-sm leading-6 shadow-sm transition duration-300 sm:max-w-[78%] ${
                  msg.role === "user"
                    ? "bg-black text-white shadow-[0_14px_22px_rgba(0,0,0,0.18)]"
                    : "border border-accent/25 bg-white/85 text-ink"
                }`}
              >
                <p>{msg.content}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {msg.sources.map((src) => (
                      <Link
                        key={`${msg.id}-${src.source_id}`}
                        href={`/books/${src.book_id}`}
                        className="rounded-full border border-black/10 bg-white px-3 py-1 text-xs text-body hover:bg-black/5"
                      >
                        {src.source_id} {src.book_title}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start">
              <div className="rounded-2xl border border-accent/20 bg-white/80 px-4 py-3 text-sm text-ink">
                AI is thinking <LoadingDots />
              </div>
            </div>
          )}
        </div>

        <form onSubmit={onSubmit} className="mt-4 flex items-center gap-2">
          <input
            className="glass-input"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about themes, summaries, or recommendations"
          />
          <button type="submit" className="primary-btn min-w-[92px]" disabled={loading || !question.trim()}>
            Ask AI
          </button>
        </form>
      </GlassPanel>
    </div>
  );
}
