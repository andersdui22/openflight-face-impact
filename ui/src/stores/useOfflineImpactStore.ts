import { create } from 'zustand';
import { isOfflineImpactEvidence, type OfflineImpactEvidence } from '../types/offlineImpactEvidence';

type OfflineImpactState = {
  sessionId: string | null;
  entries: OfflineImpactEvidence[];
  ingest: (payload: unknown) => void;
  restore: (sessionId: string, entries: OfflineImpactEvidence[]) => void;
  clear: () => void;
};

const MAX_ENTRIES = 100;

export const useOfflineImpactStore = create<OfflineImpactState>((set) => ({
  sessionId: null,
  entries: [],
  ingest: (payload) => {
    if (!isOfflineImpactEvidence(payload)) return;
    set((state) => {
      if (state.sessionId !== null && state.sessionId !== payload.session_id) {
        return { sessionId: payload.session_id, entries: [payload] };
      }
      const existing = state.entries.find((item) => item.shot_id === payload.shot_id);
      if (existing) {
        // A shot is immutable once accepted or rejected: replayed network events
        // must not silently revise evidence.
        return state;
      }
      return {
        sessionId: payload.session_id,
        entries: [...state.entries, payload].slice(-MAX_ENTRIES),
      };
    });
  },
  restore: (sessionId, entries) => set({ sessionId, entries: entries.slice(-MAX_ENTRIES) }),
  clear: () => set({ sessionId: null, entries: [] }),
}));
