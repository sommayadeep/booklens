export type Book = {
  id: number;
  title: string;
  author: string;
  rating: number | null;
  reviews_count: number | null;
  description: string;
  book_url: string;
  image_url: string;
  summary: string;
  genre: string;
  sentiment?: string;
  ai_processed: boolean;
  metadata?: Record<string, string | number | boolean | null>;
  created_at?: string;
  updated_at?: string;
};

export type BookStats = {
  total_books: number;
  ai_processed: number;
  text_chunks: number;
  genres: number;
  qa_sessions: number;
};

export type BookListResponse = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Book[];
};

export type SourceCitation = {
  source_id: string;
  book_id: number;
  book_title: string;
  book_url: string;
  chunk_index: number;
  snippet: string;
};

export type RagAnswer = {
  id: number;
  answer: string;
  sources: SourceCitation[];
  book_id: number | null;
};
