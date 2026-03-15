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
      <div className="flex min-h-[40vh] items-center justify-center">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-slate-200 border-t-emerald-600" />
      </div>
    );
  }

  if (error || !data?.success || !data.data) {
    return (
      <div className="mx-auto max-w-lg rounded-xl bg-amber-50 p-6 text-center">
        <p className="text-amber-800">Could not load this analysis.</p>
        <Link href="/" className="mt-4 inline-block text-emerald-600 underline">
          Start over
        </Link>
      </div>
    );
  }

  const result = data.data;
  const history = historyData?.data?.sessions ?? result.history ?? [];
  const lowConfidence = (result.top_confidence ?? 0) < 0.4;

  return (
    <div className="mx-auto max-w-2xl space-y-8 pb-12">
      {lowConfidence && (
        <div className="rounded-xl bg-amber-50 p-4 text-sm text-amber-800">
          Unable to determine condition clearly. For better results, retake in good
          lighting with your face centred.
        </div>
      )}
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-semibold text-slate-800">Your skin report</h1>
        <Link
          href="/"
          className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
        >
          Retake
        </Link>
      </div>

      <ScoreGauge score={result.skin_health_score} />

      <div className="flex flex-wrap items-center gap-2">
        <span className="text-sm text-slate-600">Severity:</span>
        <SeverityBadge tier={result.severity_tier} />
        {result.top_condition && (
          <span className="text-sm text-slate-600">
            Top: {result.top_condition} ({Math.round((result.top_confidence ?? 0) * 100)}%)
          </span>
        )}
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <ConditionsChart predictions={result.predictions ?? []} />
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <RecommendationsPanel recommendations={result.recommendations ?? []} />
      </div>

      {history.length >= 2 && (
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <HistoryChart sessions={history} />
        </div>
      )}

      <p className="text-center text-xs text-slate-500">
        This is not a medical diagnosis. Consult a dermatologist for professional advice.
      </p>
    </div>
  );
}
