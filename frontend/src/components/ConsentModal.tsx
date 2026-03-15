"use client";

import { useSessionStore } from "@/store/sessionStore";

const DISCLAIMER =
  "This tool is for general skin awareness only and does not replace professional dermatological advice. Always consult a doctor for medical concerns.";

export function ConsentModal() {
  const consentGivenAt = useSessionStore((s) => s.consentGivenAt);
  const setConsent = useSessionStore((s) => s.setConsent);

  if (consentGivenAt) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="max-w-md rounded-2xl bg-white p-6 shadow-xl">
        <h2 className="text-xl font-semibold text-slate-800">
          Privacy &amp; consent
        </h2>
        <p className="mt-3 text-sm text-slate-600">
          We use your photo only to run the skin analysis. Images may be stored
          server-side for up to 30 days unless you opt in to longer history.
          We do not share your data with third parties.
        </p>
        <p className="mt-2 text-sm font-medium text-amber-800">
          {DISCLAIMER}
        </p>
        <button
          type="button"
          onClick={setConsent}
          className="mt-6 w-full rounded-xl bg-emerald-600 px-4 py-3 font-medium text-white transition hover:bg-emerald-700"
        >
          I understand
        </button>
      </div>
    </div>
  );
}
