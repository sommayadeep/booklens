import { GlassPanel } from "@/components/glass-panel";

type StatsCardProps = {
  label: string;
  value: string | number;
};

export function StatsCard({ label, value }: StatsCardProps) {
  return (
    <GlassPanel className="animate-fadeUp p-5 transition duration-300 hover:-translate-y-0.5 hover:shadow-float">
      <div className="mb-4 h-[1px] w-full bg-gradient-to-r from-transparent via-black/10 to-transparent" />
      <p className="text-xs uppercase tracking-[0.2em] text-muted">{label}</p>
      <p className="mt-3 bg-gradient-to-b from-ink to-ink/70 bg-clip-text text-3xl font-semibold text-transparent">
        {value}
      </p>
    </GlassPanel>
  );
}
