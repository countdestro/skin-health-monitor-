"use client";

interface ScoreGaugeProps {
  score: number;
  className?: string;
}

const ZONES = [
  { max: 19, color: "#b91c1c", label: "Severe" },
  { max: 39, color: "#ef4444", label: "Poor" },
  { max: 54, color: "#f97316", label: "Moderate" },
  { max: 69, color: "#f59e0b", label: "Fair" },
  { max: 84, color: "#00B894", label: "Good" },
  { max: 100, color: "#00B894", label: "Excellent" },
];

function getColor(score: number) {
  const zone = ZONES.find((z) => score <= z.max);
  return zone?.color ?? ZONES[ZONES.length - 1].color;
}

export function ScoreGauge({ score, className = "" }: ScoreGaugeProps) {
  const clamped = Math.max(0, Math.min(100, score));
  const color = getColor(clamped);
  const dashLength = (clamped / 100) * 125;

  return (
    <div className={`flex flex-col items-center ${className}`}>
      <div className="relative h-44 w-44">
        <svg viewBox="0 0 120 80" className="h-full w-full">
          <defs>
            <linearGradient id="gaugeTrack" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#e4e4e7" />
              <stop offset="100%" stopColor="#f4f4f5" />
            </linearGradient>
          </defs>
          <path
            d="M 22 68 A 42 42 0 0 1 98 68"
            fill="none"
            stroke="url(#gaugeTrack)"
            strokeWidth="10"
            strokeLinecap="round"
          />
          <path
            d="M 22 68 A 42 42 0 0 1 98 68"
            fill="none"
            stroke={color}
            strokeWidth="10"
            strokeLinecap="round"
            strokeDasharray={`${dashLength} 130`}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div
          className="absolute left-1/2 top-1/2 flex -translate-x-1/2 -translate-y-1/2 flex-col items-center"
          style={{ color }}
        >
          <span className="font-display text-4xl font-bold tabular-nums">
            {Math.round(clamped)}
          </span>
          <span className="text-xs font-medium opacity-80">/ 100</span>
        </div>
      </div>
      <p className="mt-3 text-sm font-medium text-surface-500">Skin health score</p>
    </div>
  );
}
