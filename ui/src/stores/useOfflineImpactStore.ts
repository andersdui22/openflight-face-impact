import { create } from 'zustand';
import { isOfflineImpactEvidence, type OfflineImpactEvidence } from '../types/offlineImpactEvidence';

type OfflineImpactState = {
  sessionId: string | null;
  entries: OfflineImpactEvidence[];
  archivedEntries: OfflineImpactEvidence[];
  ingest: (payload: unknown) => void;
  restore: (sessionId: string, entries: OfflineImpactEvidence[]) => void;
  clear: () => void;
};

const MAX_ENTRIES = 100;

export const useOfflineImpactStore = create<OfflineImpactState>((set) => ({
  sessionId: null,
  entries: [],
  archivedEntries: [],
  ingest: (payload) => {
    if (!isOfflineImpactEvidence(payload)) return;
    set((state) => {
      if (state.sessionId !== null && state.sessionId !== payload.session_id) {
        return { sessionId: payload.session_id, entries: [payload], archivedEntries: [] };
      }
      const existing = state.entries.find((item) => item.shot_id === payload.shot_id);
      if (existing) {
        // A shot is immutable once accepted or rejected: replayed network events
        // must not silently revise evidence.
        return state;
      }
      const entries = [...state.entries, payload].slice(-MAX_ENTRIES);
      return {
        sessionId: payload.session_id,
        entries,
        archivedEntries: state.archivedEntries.filter((entry) => entries.includes(entry)),
      };
    });
  },
  restore: (sessionId, entries) => {
    const recentEntries = entries.slice(-MAX_ENTRIES);
    set({ sessionId, entries: recentEntries, archivedEntries: recentEntries });
  },
  clear: () => set({ sessionId: null, entries: [], archivedEntries: [] }),
}));
