"use client";

import { useState, useCallback } from "react";
import { ConsentModal } from "@/components/ConsentModal";
import { CaptureScreen } from "@/components/CaptureScreen";

export default function HomePage() {
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleError = useCallback((message: string) => {
    setErrorMessage(message);
  }, []);

  return (
    <main className="min-h-screen bg-gradient-to-b from-slate-50 to-slate-100">
      <ConsentModal />
      <div className="mx-auto max-w-2xl px-4 py-8">
        <header className="mb-8 text-center">
          <h1 className="text-2xl font-bold text-slate-800">
            AI Skin Health Monitor
          </h1>
          <p className="mt-2 text-sm text-slate-600">
            Capture or upload a photo for a non-diagnostic skin analysis
          </p>
        </header>

        {errorMessage && (
          <div className="mb-4 rounded-xl bg-red-50 p-4 text-sm text-red-800">
            <p>{errorMessage}</p>
            <button
              type="button"
              onClick={() => setErrorMessage(null)}
              className="mt-2 font-medium underline"
            >
              Dismiss
            </button>
          </div>
        )}

        <CaptureScreen onError={handleError} />
      </div>
    </main>
  );
}
