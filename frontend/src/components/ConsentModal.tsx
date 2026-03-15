"use client";

import { useSessionStore } from "@/store/sessionStore";

const DISCLAIMER =
  "This tool is for general skin awareness only and does not replace professional dermatological advice. Always consult a doctor for medical concerns.";

export function ConsentModal() {
  const consentGivenAt = useSessionStore((s) => s.consentGivenAt);
  const setConsent = useSessionStore((s) => s.setConsent);

  if (consentGivenAt) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-zinc-900/70 p-4 backdrop-blur-sm">
      <div className="w-full max-w-md rounded-3xl border border-zinc-100 bg-white p-8 shadow-2xl animate-fade-in">
        <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary-100">
          <svg className="h-6 w-6 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.623 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.285z" />
          </svg>
        </div>
        <h2 className="font-display text-xl font-semibold text-zinc-900">
          Privacy &amp; consent
        </h2>
        <p className="mt-3 text-sm leading-relaxed text-zinc-600">
          We use your photo only to run the skin analysis. Images may be stored
          server-side for up to 30 days unless you opt in to longer history.
          We do not share your data with third parties.
        </p>
        <p className="mt-4 rounded-xl bg-amber-50 px-3 py-2.5 text-sm font-medium text-amber-800">
          {DISCLAIMER}
        </p>
        <button
          type="button"
          onClick={setConsent}
          className="btn-primary mt-6 w-full"
        >
          I understand
        </button>
      </div>
    </div>
  );
}
