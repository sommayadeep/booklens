"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";

import { GlassPanel } from "@/components/glass-panel";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/ask", label: "Ask AI" },
  { href: "/login", label: "Login" },
];

export function Navbar() {
  const pathname = usePathname();

  return (
    <GlassPanel className="sticky top-4 z-40 mx-auto mb-8 flex max-w-6xl items-center justify-between px-5 py-3 shadow-float">
      <Link href="/" className="font-serif text-xl font-semibold tracking-tight text-ink">
        BookLens
      </Link>
      <nav className="flex items-center gap-2">
        {links.map((link) => (
          <Link
            key={link.href}
            href={link.href}
            className={clsx(
              "rounded-full px-4 py-2 text-sm transition duration-300",
              pathname === link.href
                ? "bg-black text-white shadow-[0_12px_20px_rgba(0,0,0,0.22)]"
                : "text-body hover:-translate-y-0.5 hover:bg-white/75 hover:text-ink",
            )}
          >
            {link.label}
          </Link>
        ))}
      </nav>
    </GlassPanel>
  );
}
