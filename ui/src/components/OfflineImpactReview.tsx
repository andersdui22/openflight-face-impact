import { useState } from 'react';
import { socketService } from '../services/socketService';
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
  const entries = evidence ?? liveEntries;
  const [selectedShotId, setSelectedShotId] = useState<string | null>(null);
  const [demoCase, setDemoCase] = useState<'contact' | 'missing-ball'>('contact');
  const [loadingDemo, setLoadingDemo] = useState(false);
  const [demoError, setDemoError] = useState<string | null>(null);
  const selected = entries.find((entry) => entry.shot_id === selectedShotId) ?? entries[entries.length - 1];
  const accepted = entries.filter((entry) => entry.accepted);
  const validSelection =
    selected?.accepted && selected.x_mm >= -45 && selected.x_mm <= 45 && selected.y_mm >= -25 && selected.y_mm <= 25;

  async function runDemo() {
    setLoadingDemo(true);
    setDemoError(null);
    try {
      setSelectedShotId(await socketService.requestOfflineImpactDemo(demoCase));
    } catch (error) {
      setDemoError(error instanceof Error ? error.message : 'Synthetic offline replay unavailable');
    } finally {
      setLoadingDemo(false);
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
            disabled={loadingDemo}
            onChange={(event) => setDemoCase(event.target.value === 'missing-ball' ? 'missing-ball' : 'contact')}
          >
            <option value="contact">Contact</option>
            <option value="missing-ball">Missing ball</option>
          </select>
        </label>
        <button type="button" onClick={() => void runDemo()} disabled={loadingDemo}>
          {loadingDemo ? 'Running synthetic replay…' : 'Run synthetic replay'}
        </button>
      </div>
      {demoError && <p role="alert">{demoError}</p>}
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
                ? `X ${entry.x_mm} mm, Y ${entry.y_mm} mm (synthetic only)`
                : `rejected — ${entry.reason}`}
            </button>
          </li>
        ))}
      </ol>
    </section>
  );
}
