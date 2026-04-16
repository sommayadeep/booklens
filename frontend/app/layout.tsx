import type { Metadata } from "next";



import { Navbar } from "@/components/navbar";

import "./globals.css";

export const metadata: Metadata = {
  title: "BookLens | Document Intelligence Platform",
  description: "AI-powered book analysis with RAG-based Q&A",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="font-sans text-body antialiased">
        <div className="page-bg" />
        <main className="mx-auto max-w-6xl px-4 pb-16 pt-5 sm:px-6">
          <Navbar />
          {children}
        </main>
      </body>
    </html>
  );
}
