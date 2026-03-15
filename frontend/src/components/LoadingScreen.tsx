"use client";

interface LoadingScreenProps {
  messages: string[];
  currentPhase: number;
}

export function LoadingScreen({ messages, currentPhase }: LoadingScreenProps) {
  return (
    <div className="flex min-h-[280px] flex-col items-center justify-center gap-6 rounded-2xl bg-slate-100 p-8">
      <div className="h-12 w-12 animate-spin rounded-full border-4 border-slate-300 border-t-emerald-600" />
      <p className="text-center font-medium text-slate-700">
        {messages[currentPhase] ?? messages[messages.length - 1]}
      </p>
    </div>
  );
}
