import clsx from "clsx";
import type { PropsWithChildren } from "react";

type GlassPanelProps = PropsWithChildren<{
  className?: string;
}>;

export function GlassPanel({ className, children }: GlassPanelProps) {
  return (
    <div className={clsx("glass-shell rounded-panel", className)}>
      <div className="pointer-events-none absolute -left-10 top-1/2 h-24 w-24 -translate-y-1/2 rounded-full bg-sand/30 blur-2xl" />
      <div className="relative z-[1]">{children}</div>
    </div>
  );
}
