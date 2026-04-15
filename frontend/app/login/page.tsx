"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { GlassPanel } from "@/components/glass-panel";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  function onSubmit(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!email.trim() || !password.trim()) {
      return;
    }

    localStorage.setItem("booklens_session", JSON.stringify({ email, loggedInAt: new Date().toISOString() }));
    router.push("/");
  }

  return (
    <div className="mx-auto flex min-h-[70vh] max-w-md items-center justify-center">
      <GlassPanel className="glass-grid w-full p-7 sm:p-8">
        <p className="text-xs uppercase tracking-[0.2em] text-muted">Welcome Back</p>
        <h1 className="heading-font mt-2 text-3xl text-ink">Login to BookLens</h1>
        <p className="mt-2 text-sm text-body">Secure access to your AI-powered document workspace.</p>

        <form onSubmit={onSubmit} className="mt-6 space-y-4">
          <div>
            <label className="mb-1 block text-xs uppercase tracking-[0.15em] text-muted">Email</label>
            <input
              type="email"
              className="glass-input"
              placeholder="you@booklens.ai"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label className="mb-1 block text-xs uppercase tracking-[0.15em] text-muted">Password</label>
            <input
              type="password"
              className="glass-input"
              placeholder="Enter password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button className="primary-btn w-full">Continue</button>
        </form>
      </GlassPanel>
    </div>
  );
}
