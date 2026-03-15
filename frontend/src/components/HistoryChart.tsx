"use client";

import type { SessionHistoryItem } from "@/types/api";

interface HistoryChartProps {
  sessions: SessionHistoryItem[];
}

export function HistoryChart({ sessions }: HistoryChartProps) {
  if (sessions.length < 2) return null;

  const sorted = [...sessions].sort(
    (a, b) =>
      new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
  );
  const scores = sorted.map((s) => s.skin_health_score);
  const min = Math.min(...scores, 0);
  const max = Math.max(...scores, 100);
  const range = max > min ? max - min : 100;

  return (
    <div className="space-y-4">
      <h3 className="font-display text-sm font-semibold text-zinc-900">
        Score over time
      </h3>
      <div className="flex h-28 items-end gap-1.5 rounded-xl bg-surface-50 p-3">
        {scores.map((score, i) => (
          <div
            key={sorted[i].id}
            className="flex flex-1 flex-col items-center gap-1"
          >
            <div
              className="w-full min-w-[8px] rounded-t-lg bg-teal transition-all duration-500"
              style={{
                height: `${(range ? (score - min) / range : 0.5) * 70 + 14}px`,
              }}
              title={`${new Date(sorted[i].created_at).toLocaleDateString()}: ${score}`}
            />
            <span className="text-[10px] font-medium tabular-nums text-surface-500">
              {score}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
