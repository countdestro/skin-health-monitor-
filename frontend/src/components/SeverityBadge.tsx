"use client";

const SEVERITY_STYLES: Record<string, { bg: string; text: string }> = {
  Excellent: { bg: "bg-green-100", text: "text-green-800" },
  Good: { bg: "bg-green-50", text: "text-green-700" },
  Fair: { bg: "bg-amber-100", text: "text-amber-800" },
  Moderate: { bg: "bg-orange-100", text: "text-orange-800" },
  Poor: { bg: "bg-red-100", text: "text-red-800" },
  Severe: { bg: "bg-red-200", text: "text-red-900" },
};

export function SeverityBadge({ tier }: { tier: string }) {
  const style = SEVERITY_STYLES[tier] ?? {
    bg: "bg-slate-100",
    text: "text-slate-800",
  };
  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-sm font-medium ${style.bg} ${style.text}`}
    >
      {tier}
    </span>
  );
}
