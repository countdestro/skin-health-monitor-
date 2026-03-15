"use client";

import { useState, useCallback, useEffect } from "react";
import { ConsentModal } from "@/components/ConsentModal";
import { CaptureScreen } from "@/components/CaptureScreen";

const TAGLINE = "Capture or upload a photo for a quick, AI-powered skin analysis and personalised tips.";

export default function HomePage() {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [taglineVisible, setTaglineVisible] = useState(false);

  useEffect(() => {
    const t = setTimeout(() => setTaglineVisible(true), 400);
    return () => clearTimeout(t);
  }, []);

  const handleError = useCallback((message: string) => {
    setErrorMessage(message);
  }, []);

  return (
    <main className="min-h-screen bg-warm-gray">
      <ConsentModal />
      <div className="mx-auto max-w-[480px] px-4 pb-12 pt-6">
        <header className="mb-8 text-center">
          <div
            className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/60 bg-white/70 px-4 py-2 text-sm font-medium text-zinc-600 shadow-sm backdrop-blur-md"
            style={{ boxShadow: "0 2px 12px rgba(0,0,0,0.04)" }}
          >
            <span className="h-1.5 w-1.5 rounded-full bg-teal" />
            Non-diagnostic · For awareness only
          </div>
          <h1 className="font-display text-3xl font-bold tracking-tight text-zinc-900 sm:text-4xl">
            AI{" "}
            <span className="bg-gradient-to-r from-teal to-teal-dark bg-clip-text text-transparent">
              Skin
            </span>{" "}
            Health Monitor
          </h1>
          <p
            className={`mt-4 max-w-sm mx-auto text-base text-zinc-600 transition-all duration-500 ${
              taglineVisible ? "animate-fade-in opacity-100" : "opacity-0"
            }`}
          >
            {TAGLINE}
          </p>
        </header>

        {errorMessage && (
          <div className="mb-4 rounded-2xl border border-red-100 bg-red-50/90 p-4 text-sm text-red-800 shadow-card backdrop-blur-sm">
            <p>{errorMessage}</p>
            <button
              type="button"
              onClick={() => setErrorMessage(null)}
              className="mt-2 font-medium text-red-700 hover:underline"
            >
              Dismiss
            </button>
          </div>
        )}

        <div className="animate-slide-up">
          <CaptureScreen onError={handleError} />
        </div>
      </div>
    </main>
  );
}
