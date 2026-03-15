import { create } from "zustand";
import { persist } from "zustand/middleware";
import { v4 as uuidv4 } from "uuid";

export interface SessionState {
  sessionId: string | null;
  consentGivenAt: string | null;
  setConsent: () => void;
  getOrCreateSessionId: () => string;
  clearSession: () => void;
}

export const useSessionStore = create<SessionState>()(
  persist(
    (set, get) => ({
      sessionId: null,
      consentGivenAt: null,
      setConsent: () =>
        set({
          consentGivenAt: new Date().toISOString(),
          sessionId: get().sessionId ?? uuidv4(),
        }),
      getOrCreateSessionId: () => {
        let id = get().sessionId;
        if (!id) {
          id = uuidv4();
          set({ sessionId: id });
        }
        return id;
      },
      clearSession: () => set({ sessionId: null, consentGivenAt: null }),
    }),
    { name: "skin-health-session" }
  )
);
