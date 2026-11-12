import { isOfflineSessionAnalysis, type OfflineSessionAnalysis } from '../types/offlineSessionAnalysis';
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

export async function loadOfflineSession(sessionId: string): Promise<OfflineSessionAnalysis> {
  const response = await fetch(`${offlineSessionUrl(sessionId)}?analysis=1`, { cache: 'no-store' });
  if (!response.ok) throw new Error('Saved session could not be loaded');
  const data: unknown = await response.json();
  if (!isOfflineSessionAnalysis(data, sessionId)) throw new Error('Saved session analysis is invalid');
  return data;
}
