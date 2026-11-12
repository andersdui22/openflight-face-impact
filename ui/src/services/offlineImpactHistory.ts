import { isOfflineImpactEvidence, type OfflineImpactEvidence } from '../types/offlineImpactEvidence';
import { getServerOrigin } from '../utils/serverOrigin';

type SessionSummary = { session_id: string; shot_count: number; saved_at_utc: string };

export function offlineSessionUrl(sessionId: string, download = false): string {
  return `${getServerOrigin()}/api/face-impact/sessions/${encodeURIComponent(sessionId)}${download ? '?download=1' : ''}`;
}

export async function listOfflineSessions(): Promise<SessionSummary[]> {
  const response = await fetch(`${getServerOrigin()}/api/face-impact/sessions`, { cache: 'no-store' });
  if (!response.ok) throw new Error('Saved session history unavailable');
  const data = await response.json();
  if (
    data?.schema_version !== 1 ||
    !Array.isArray(data.sessions) ||
    !data.sessions.every(
      (entry: Partial<SessionSummary> | null) =>
        entry &&
        typeof entry.session_id === 'string' &&
        !!entry.session_id &&
        Number.isSafeInteger(entry.shot_count) &&
        typeof entry.saved_at_utc === 'string'
    )
  )
    throw new Error('Saved session history is invalid');
  return data.sessions;
}

export async function loadOfflineSession(sessionId: string): Promise<OfflineImpactEvidence[]> {
  const response = await fetch(offlineSessionUrl(sessionId), { cache: 'no-store' });
  if (!response.ok) throw new Error('Saved session could not be loaded');
  const data = await response.json();
  if (
    data?.schema_version !== 1 ||
    data.source !== 'offline_synthetic_analysis' ||
    data.session_id !== sessionId ||
    !Array.isArray(data.shots) ||
    !data.shots.length
  )
    throw new Error('Saved session is invalid');

  const entries: unknown[] = data.shots.map((shot: { evidence?: unknown } | null) => shot?.evidence);
  if (!entries.every(isOfflineImpactEvidence) || entries.some((entry) => entry.session_id !== sessionId)) {
    throw new Error('Saved shot evidence is invalid');
  }
  if (new Set(entries.map((entry) => entry.shot_id)).size !== entries.length) {
    throw new Error('Saved shot identities are duplicated');
  }
  return entries;
}
