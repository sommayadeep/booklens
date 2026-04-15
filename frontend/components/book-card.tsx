import Image from "next/image";
import Link from "next/link";

import { GlassPanel } from "@/components/glass-panel";
import type { Book } from "@/types";

type BookCardProps = {
  book: Book;
};

export function BookCard({ book }: BookCardProps) {
  const ratingLabel = book.rating ? `${book.rating.toFixed(1)} / 5` : "N/A";

  return (
    <Link href={`/books/${book.id}`} className="group block">
      <GlassPanel className="h-full overflow-hidden p-4 transition duration-300 group-hover:scale-[1.03] group-hover:shadow-float">
        <div className="relative mb-4 h-44 w-full overflow-hidden rounded-2xl bg-fog">
          <div className="pointer-events-none absolute inset-0 z-[1] bg-gradient-to-t from-black/20 via-transparent to-white/20" />
          {book.image_url ? (
            <Image
              src={book.image_url}
              alt={book.title}
              fill
              className="object-cover transition duration-300 group-hover:scale-105"
              unoptimized
            />
          ) : (
            <div className="flex h-full items-center justify-center text-sm text-muted">No Cover</div>
          )}
        </div>

        <p className="mb-1 line-clamp-1 text-lg font-semibold text-ink">{book.title}</p>
        <p className="mb-3 line-clamp-1 text-sm text-body">by {book.author || "Unknown"}</p>

        <div className="mb-3 flex items-center justify-between text-sm">
          <span className="rounded-full border border-black/10 bg-white/70 px-3 py-1 text-ink">
            Rating: {ratingLabel}
          </span>
          <span className="text-muted">{book.reviews_count ?? 0} reviews</span>
        </div>

        <p className="line-clamp-3 text-sm text-body">{book.description || "No description available."}</p>

        <div className="mt-4 inline-flex rounded-full border border-black/10 bg-sand/70 px-3 py-1 text-xs font-medium text-ink">
          {book.genre || "General"}
        </div>
      </GlassPanel>
    </Link>
  );
}
