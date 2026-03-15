"use client";

const SEVERITY_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  Excellent: { bg: "bg-primary-50", text: "text-primary-800", border: "border-primary-200" },
  Good: { bg: "bg-teal-50", text: "text-teal-800", border: "border-teal-200" },
  Fair: { bg: "bg-amber-50", text: "text-amber-800", border: "border-amber-200" },
  Moderate: { bg: "bg-orange-50", text: "text-orange-800", border: "border-orange-200" },
  Poor: { bg: "bg-red-50", text: "text-red-800", border: "border-red-200" },
  Severe: { bg: "bg-red-100", text: "text-red-900", border: "border-red-300" },
};

export function SeverityBadge({ tier }: { tier: string }) {
  const style = SEVERITY_STYLES[tier] ?? {
    bg: "bg-surface-100",
    text: "text-zinc-800",
    border: "border-surface-200",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full border px-3.5 py-1.5 text-sm font-semibold ${style.bg} ${style.text} ${style.border}`}
    >
      {tier}
    </span>
  );
}
