"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { getSession, getHistory } from "@/lib/api";
import { useSessionStore } from "@/store/sessionStore";
import { ScoreGauge } from "@/components/ScoreGauge";
import { ConditionsChart } from "@/components/ConditionsChart";
import { SeverityBadge } from "@/components/SeverityBadge";
import { RecommendationsPanel } from "@/components/RecommendationsPanel";
import { HistoryChart } from "@/components/HistoryChart";
import { MetricPill } from "@/components/MetricPill";

export default function ResultsPage() {
  const params = useParams();
  const id = params.id as string;
  const sessionId = useSessionStore((s) => s.sessionId ?? s.getOrCreateSessionId());

  const { data, isLoading, error } = useQuery({
    queryKey: ["session", id],
    queryFn: () => getSession(id),
    enabled: !!id,
  });

  const { data: historyData } = useQuery({
    queryKey: ["history", sessionId],
    queryFn: () => getHistory(sessionId),
    enabled: !!sessionId && !!data?.success,
  });

  if (isLoading) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center bg-warm-gray">
        <div className="flex flex-col items-center gap-4">
          <div className="h-12 w-12 animate-spin rounded-2xl border-2 border-teal/20 border-t-teal" />
          <p className="text-sm font-medium text-zinc-500">Loading your report…</p>
        </div>
      </div>
    );
  }

  if (error || !data?.success || !data.data) {
    return (
      <div className="flex min-h-[50vh] items-center justify-center bg-warm-gray px-4">
        <div className="card-static max-w-md text-center">
          <p className="text-zinc-700">Could not load this analysis.</p>
          <Link href="/" className="btn-primary mt-4 inline-flex">
            Start over
          </Link>
        </div>
      </div>
    );
  }

  const result = data.data;
  const history = historyData?.data?.sessions ?? result.history ?? [];
  const lowConfidence = (result.top_confidence ?? 0) < 0.4;
  const score = result.skin_health_score ?? 0;
  const hydration = Math.min(100, score + 5);
  const oiliness = Math.min(100, Math.max(0, 100 - score * 0.7));
  const sensitivity = Math.min(100, Math.max(0, 100 - score * 0.5));

  return (
    <main className="min-h-screen bg-warm-gray pb-16">
      <div className="mx-auto max-w-[480px] px-4 pt-4">
        {lowConfidence && (
          <div className="mb-4 rounded-2xl border border-amber-200 bg-amber-50/90 p-4 text-sm text-amber-800">
            Unable to determine condition clearly. For better results, retake in good
            lighting with your face centred.
          </div>
        )}

        <div className="mb-4 flex items-center justify-between">
          <h1 className="font-display text-xl font-bold tracking-tight text-zinc-900">
            Your skin report
          </h1>
          <Link href="/" className="btn-secondary">
            Retake
          </Link>
        </div>

        {/* Results panel: white card, teal header, slide-up */}
        <div className="animate-slide-up-slow overflow-hidden rounded-2xl bg-white shadow-lg">
          <div className="bg-teal px-4 py-3">
            <h2 className="font-display text-sm font-semibold uppercase tracking-wide text-white">
              Skin Analysis
            </h2>
          </div>
          <div className="p-4">
            <section className="flex flex-col items-center py-4">
              <ScoreGauge score={score} />
              <div className="mt-4 flex flex-wrap items-center justify-center gap-2">
                <SeverityBadge tier={result.severity_tier} />
                {result.top_condition && (
                  <span className="text-sm text-zinc-500">
                    Top: {result.top_condition} ({Math.round((result.top_confidence ?? 0) * 100)}%)
                  </span>
                )}
              </div>
            </section>

            <section className="space-y-4 border-t border-zinc-100 pt-4">
              <h3 className="text-sm font-semibold text-zinc-800">Metrics</h3>
              <MetricPill label="Hydration" value={hydration} />
              <MetricPill label="Oiliness" value={oiliness} />
              <MetricPill label="Sensitivity" value={sensitivity} />
            </section>

            <section className="border-t border-zinc-100 pt-4">
              <ConditionsChart predictions={result.predictions ?? []} />
            </section>

            <section className="border-t border-zinc-100 pt-4">
              <RecommendationsPanel recommendations={result.recommendations ?? []} />
            </section>

            {history.length >= 2 && (
              <section className="border-t border-zinc-100 pt-4">
                <HistoryChart sessions={history} />
              </section>
            )}
          </div>
        </div>

        <p className="mt-6 text-center text-xs text-zinc-500">
          Not a medical diagnosis. Consult a dermatologist for professional advice.
        </p>
      </div>
    </main>
  );
}
