"use client";

import type { ConditionPrediction } from "@/types/api";

interface ConditionsChartProps {
  predictions: ConditionPrediction[];
  minConfidence?: number;
}

const THRESHOLD = 0.1;

export function ConditionsChart({
  predictions,
  minConfidence = THRESHOLD,
}: ConditionsChartProps) {
  const filtered = predictions.filter((p) => p.confidence >= minConfidence);
  const maxConf = Math.max(...filtered.map((p) => p.confidence), 0.01);

  return (
    <div className="space-y-4">
      <h3 className="font-display text-sm font-semibold text-zinc-900">
        Detected conditions
      </h3>
      {filtered.length === 0 ? (
        <p className="text-sm text-surface-500">
          No conditions above 10% confidence.
        </p>
      ) : (
        <div className="space-y-3">
          {filtered.map((p) => (
            <div key={p.condition} className="flex items-center gap-3">
              <span className="w-28 shrink-0 truncate text-sm font-medium text-zinc-700">
                {p.condition}
              </span>
              <div className="h-7 flex-1 overflow-hidden rounded-lg bg-surface-100">
                <div
                  className="h-full rounded-lg bg-teal transition-all duration-500"
                  style={{
                    width: `${(p.confidence / maxConf) * 100}%`,
                  }}
                />
              </div>
              <span className="w-11 text-right text-sm font-semibold tabular-nums text-zinc-600">
                {Math.round(p.confidence * 100)}%
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
