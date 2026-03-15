"use client";

interface MetricPillProps {
  label: string;
  value: number;
  className?: string;
}

export function MetricPill({ label, value, className = "" }: MetricPillProps) {
  const clamped = Math.max(0, Math.min(100, value));
  return (
    <div className={`space-y-2 ${className}`}>
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-zinc-700">{label}</span>
        <span className="text-sm font-semibold tabular-nums text-teal">{clamped}%</span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-zinc-100">
        <div
          className="h-full rounded-full bg-teal transition-all duration-500 ease-out"
          style={{ width: `${clamped}%` }}
        />
      </div>
    </div>
  );
}
