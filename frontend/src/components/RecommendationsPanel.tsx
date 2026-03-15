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
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-slate-800">Recommendations</h3>
      <div className="space-y-2">
        {categories.map((cat) => {
          const items = byCategory[cat];
          const isOpen = expanded[cat] ?? true;
          return (
            <div key={cat} className="rounded-xl border border-slate-200 bg-white">
              <button
                type="button"
                onClick={() => setExpanded((e) => ({ ...e, [cat]: !isOpen }))}
                className="flex w-full items-center justify-between px-4 py-3 text-left font-medium text-slate-800"
              >
                {cat}
                <span className="text-slate-400">{isOpen ? "−" : "+"}</span>
              </button>
              {isOpen && (
                <ul className="border-t border-slate-100 px-4 py-2">
                  {items.map((r, i) => (
                    <li key={i} className="py-1 text-sm text-slate-600">
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
