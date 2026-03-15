"use client";

interface ScoreGaugeProps {
  score: number;
  className?: string;
}

const ZONES = [
  { max: 19, color: "#922B21", label: "Severe" },
  { max: 39, color: "#E74C3C", label: "Poor" },
  { max: 54, color: "#E67E22", label: "Moderate" },
  { max: 69, color: "#F39C12", label: "Fair" },
  { max: 84, color: "#A9DFBF", label: "Good" },
  { max: 100, color: "#2ECC71", label: "Excellent" },
];

function getColor(score: number) {
  const zone = ZONES.find((z) => score <= z.max);
  return zone?.color ?? ZONES[ZONES.length - 1].color;
}

export function ScoreGauge({ score, className = "" }: ScoreGaugeProps) {
  const clamped = Math.max(0, Math.min(100, score));
  const color = getColor(clamped);

  return (
    <div className={`flex flex-col items-center ${className}`}>
      <div className="relative h-40 w-40">
        <svg viewBox="0 0 120 80" className="h-full w-full">
          <path
            d="M 20 70 A 40 40 0 0 1 100 70"
            fill="none"
            stroke="#e2e8f0"
            strokeWidth="12"
            strokeLinecap="round"
          />
          <path
            d="M 20 70 A 40 40 0 0 1 100 70"
            fill="none"
            stroke={color}
            strokeWidth="12"
            strokeLinecap="round"
            strokeDasharray={`${(clamped / 100) * 125} 125`}
            className="transition-all duration-1000 ease-out"
          />
        </svg>
        <div
          className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-3xl font-bold"
          style={{ color }}
        >
          {Math.round(clamped)}
        </div>
      </div>
      <p className="mt-2 text-sm font-medium text-slate-600">Skin health score</p>
    </div>
  );
}
