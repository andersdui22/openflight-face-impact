import { useId, useState } from 'react';
import { socketService } from '../services/socketService';
import { listOfflineSessions, loadOfflineSession, offlineSessionUrl } from '../services/offlineImpactHistory';
import { useOfflineImpactStore } from '../stores/useOfflineImpactStore';
import type { OfflineImpactEvidence } from '../types/offlineImpactEvidence';
import { FaceImpactView } from './FaceImpactView';

// Reference outline is synthetic and illustrative, never a camera-calibrated face.
const referenceFace: [number, number][] = [
  [-45, -25],
  [45, -25],
  [45, 25],
  [-45, 25],
];

export function OfflineImpactReview({ evidence }: { evidence?: OfflineImpactEvidence[] } = {}) {
  const liveEntries = useOfflineImpactStore((state) => state.entries);
  const sessionId = useOfflineImpactStore((state) => state.sessionId);
  const entries = evidence ?? liveEntries;
  const [selectedShotId, setSelectedShotId] = useState<string | null>(null);
  const [demoCase, setDemoCase] = useState<'contact' | 'missing-ball'>('contact');
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [demoError, setDemoError] = useState<string | null>(null);
  const [sessions, setSessions] = useState<Awaited<ReturnType<typeof listOfflineSessions>>>([]);
  const [savedSession, setSavedSession] = useState('');
  const [historyOpen, setHistoryOpen] = useState(false);
  const [historyBusy, setHistoryBusy] = useState(false);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const savedSessionLabelId = useId();
  const selected = entries.find((entry) => entry.shot_id === selectedShotId) ?? entries[entries.length - 1];
  const accepted = entries.filter((entry) => entry.accepted);
  const validSelection =
    selected?.accepted && selected.x_mm >= -45 && selected.x_mm <= 45 && selected.y_mm >= -25 && selected.y_mm <= 25;

  async function runDemo(newSession = false) {
    setLoadingDemo(true);
    setDemoError(null);
    try {
      const target = newSession
        ? null
        : sessionId === 'synthetic-offline-demo-v1'
          ? undefined
          : (sessionId ?? undefined);
      setSelectedShotId(await socketService.requestOfflineImpactDemo(demoCase, target));
      if (historyOpen) {
        await refreshSessions(newSession ? useOfflineImpactStore.getState().sessionId : null);
      }
    } catch (error) {
      setDemoError(error instanceof Error ? error.message : 'Synthetic offline replay unavailable');
    } finally {
      setLoadingDemo(false);
    }
  }

  async function refreshSessions(preferredSession: string | null = null) {
    setHistoryBusy(true);
    setHistoryError(null);
    try {
      const available = await listOfflineSessions();
      setSessions(available);
      setSavedSession((current) => {
        const preferred = preferredSession ?? current;
        return available.some((item) => item.session_id === preferred) ? preferred : (available[0]?.session_id ?? '');
      });
    } catch (error) {
      setHistoryError(error instanceof Error ? error.message : 'Saved session history unavailable');
    } finally {
      setHistoryBusy(false);
    }
  }

  async function restoreSession() {
    setHistoryBusy(true);
    setHistoryError(null);
    try {
      const restored = await loadOfflineSession(savedSession);
      useOfflineImpactStore.getState().restore(savedSession, restored);
      setSelectedShotId(null);
    } catch (error) {
      setHistoryError(error instanceof Error ? error.message : 'Saved session could not be loaded');
    } finally {
      setHistoryBusy(false);
    }
  }

  return (
    <section className="impact-controls" aria-label="Offline synthetic impact review">
      <strong>OFFLINE SYNTHETIC REVIEW — NOT CAMERA MEASUREMENTS</strong>
      <p>
        Only versioned Python offline evidence appears here. The clubface outline is an illustrative reference, not
        calibrated camera geometry.
      </p>
      <div className="impact-controls__fields">
        <label>
          Synthetic replay case
          <select
            value={demoCase}
            disabled={loadingDemo || historyBusy}
            onChange={(event) => setDemoCase(event.target.value === 'missing-ball' ? 'missing-ball' : 'contact')}
          >
            <option value="contact">Contact</option>
            <option value="missing-ball">Missing ball</option>
          </select>
        </label>
        <button type="button" onClick={() => void runDemo()} disabled={loadingDemo || historyBusy}>
          {loadingDemo ? 'Running synthetic replay…' : 'Run synthetic replay'}
        </button>
      </div>
      {demoError && <p role="alert">{demoError}</p>}
      <details
        onToggle={(event) => {
          setHistoryOpen(event.currentTarget.open);
          if (event.currentTarget.open) void refreshSessions();
        }}
      >
        <summary>Saved synthetic sessions</summary>
        <div className="impact-controls__fields">
          <label>
            <span id={savedSessionLabelId}>Saved session</span>
            <select
              aria-labelledby={savedSessionLabelId}
              value={savedSession}
              onChange={(event) => setSavedSession(event.target.value)}
              disabled={historyBusy}
            >
              <option value="" disabled>
                Select a session
              </option>
              {sessions.map((item) => (
                <option key={item.session_id} value={item.session_id}>
                  {item.saved_at_utc.slice(0, 16).replace('T', ' ')} UTC · {item.shot_count} shot(s) · {item.session_id}
                </option>
              ))}
            </select>
          </label>
          <button type="button" disabled={historyBusy || loadingDemo} onClick={() => void refreshSessions()}>
            Refresh
          </button>
          <button
            type="button"
            disabled={!savedSession || historyBusy || loadingDemo}
            onClick={() => void restoreSession()}
          >
            Load session
          </button>
          {savedSession && <a href={offlineSessionUrl(savedSession, true)}>Export session JSON</a>}
          <button type="button" disabled={historyBusy || loadingDemo} onClick={() => void runDemo(true)}>
            Run in new session
          </button>
        </div>
        {historyError && <p role="alert">{historyError}</p>}
      </details>
      <p role="status">
        OFFLINE RESULTS: {entries.length} · SYNTHETIC ACCEPTED: {accepted.length}
      </p>
      {selected && (
        <div>
          <p>
            Selected shot: {selected.shot_id} · Session: {selected.session_id}
          </p>
          {validSelection && selected.accepted ? (
            <FaceImpactView
              polygon={referenceFace}
              result={{
                status: 'ok',
                x_mm: selected.x_mm,
                y_mm: selected.y_mm,
                horizontal_region: selected.horizontal_region,
                vertical_region: selected.vertical_region,
              }}
            />
          ) : (
            <p role="status">
              {selected.accepted
                ? 'Synthetic point lies outside the illustrative reference face; no marker displayed.'
                : `REJECTED: ${selected.reason}`}
            </p>
          )}
        </div>
      )}
      <ol aria-label="Offline synthetic shot history">
        {entries.map((entry) => (
          <li key={entry.shot_id}>
            <button type="button" onClick={() => setSelectedShotId(entry.shot_id)}>
              {entry.shot_id}:{' '}
              {entry.accepted
                ? `X ${entry.x_mm.toFixed(1)} mm, Y ${entry.y_mm.toFixed(1)} mm (synthetic only)`
                : `rejected — ${entry.reason}`}
            </button>
          </li>
        ))}
      </ol>
    </section>
  );
}
