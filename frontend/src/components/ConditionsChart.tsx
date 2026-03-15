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
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-slate-800">Detected conditions</h3>
      {filtered.length === 0 ? (
        <p className="text-sm text-slate-500">No conditions above 10% confidence.</p>
      ) : (
        <div className="space-y-2">
          {filtered.map((p) => (
            <div key={p.condition} className="flex items-center gap-2">
              <span className="w-28 shrink-0 truncate text-sm text-slate-700">
                {p.condition}
              </span>
              <div className="h-6 flex-1 overflow-hidden rounded bg-slate-200">
                <div
                  className="h-full rounded bg-emerald-500 transition-all duration-500"
                  style={{
                    width: `${(p.confidence / maxConf) * 100}%`,
                  }}
                />
              </div>
              <span className="w-10 text-right text-sm font-medium text-slate-600">
                {Math.round(p.confidence * 100)}%
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
