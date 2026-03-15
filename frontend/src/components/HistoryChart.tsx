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

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-slate-800">Score over time</h3>
      <div className="flex h-24 items-end gap-1 rounded-lg bg-slate-100 p-2">
        {scores.map((score, i) => (
          <div
            key={sorted[i].id}
            className="flex-1 rounded-t bg-emerald-500 transition-all"
            style={{
              height: `${max > min ? ((score - min) / (max - min)) * 80 + 10 : 50}%`,
            }}
            title={`${new Date(sorted[i].created_at).toLocaleDateString()}: ${score}`}
          />
        ))}
      </div>
    </div>
  );
}
