"use client";

import { useState } from "react";
import type { Recommendation } from "@/types/api";

interface RecommendationsPanelProps {
  recommendations: Recommendation[];
}

export function RecommendationsPanel({ recommendations }: RecommendationsPanelProps) {
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});

  const byCategory = recommendations.reduce<Record<string, Recommendation[]>>(
    (acc, r) => {
      (acc[r.category] = acc[r.category] ?? []).push(r);
      return acc;
    },
    {}
  );
  const categories = Object.keys(byCategory).sort();

  return (
    <div className="space-y-4">
      <h3 className="font-display text-sm font-semibold text-zinc-900">
        Personalized Tips
      </h3>
      <div className="space-y-2">
        {categories.map((cat) => {
          const items = byCategory[cat];
          const isOpen = expanded[cat] ?? true;
          return (
            <div
              key={cat}
              className="overflow-hidden rounded-xl border border-zinc-100 bg-surface-50/50 transition-colors hover:bg-surface-50"
            >
              <button
                type="button"
                onClick={() => setExpanded((e) => ({ ...e, [cat]: !isOpen }))}
                className="flex w-full items-center justify-between px-4 py-3.5 text-left font-medium text-zinc-800 transition-colors hover:bg-white/60"
              >
                {cat}
                <span
                  className={`text-surface-400 transition-transform ${isOpen ? "rotate-180" : ""}`}
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
                  </svg>
                </span>
              </button>
              {isOpen && (
                <ul className="border-t border-zinc-100 bg-white/80 px-4 py-3">
                  {items.map((r, i) => (
                    <li
                      key={i}
                      className="flex gap-2 py-2 text-sm leading-relaxed text-zinc-600"
                    >
                      <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-teal" />
                      {r.content}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
