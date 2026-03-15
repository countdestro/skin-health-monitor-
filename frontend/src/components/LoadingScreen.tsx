"use client";

interface LoadingScreenProps {
  messages: string[];
  currentPhase: number;
}

export function LoadingScreen({ messages, currentPhase }: LoadingScreenProps) {
  const label = messages[currentPhase] ?? messages[messages.length - 1];

  return (
    <div className="card flex min-h-[300px] flex-col items-center justify-center gap-8 py-12">
      <div className="relative">
        <div className="h-14 w-14 rounded-2xl border-4 border-teal/20 bg-teal-light" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-teal/20 border-t-teal" />
        </div>
      </div>
      <div className="text-center">
        <p className="font-semibold text-zinc-800">{label}</p>
        <div className="mt-3 flex justify-center gap-1.5">
          {messages.map((_, i) => (
            <span
              key={i}
              className={`h-1.5 w-1.5 rounded-full transition-colors ${
                i <= currentPhase ? "bg-teal" : "bg-zinc-200"
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
