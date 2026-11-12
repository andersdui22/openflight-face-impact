import { create } from 'zustand';
import type { SyntheticMotionPayload } from '../types/syntheticMotionPayload';

type SyntheticMotionState = {
  payload: SyntheticMotionPayload | null;
  setPayload: (payload: SyntheticMotionPayload) => void;
  clear: () => void;
};

export const useSyntheticMotionStore = create<SyntheticMotionState>((set) => ({
  payload: null,
  setPayload: (payload) => set({ payload }),
  clear: () => set({ payload: null }),
}));
