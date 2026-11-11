import { useOfflineImpactStore } from '../stores/useOfflineImpactStore';

/** Shared by the real Socket.IO listener and the UI contract tests. */
export function ingestOfflineImpactSocketEvent(data: unknown): void {
  useOfflineImpactStore.getState().ingest(data);
}
