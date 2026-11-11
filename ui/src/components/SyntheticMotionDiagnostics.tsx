/** Gate 24: read-only, explicitly synthetic camera motion diagnostics. */

import { useState } from 'react';
import { socketService } from '../services/socketService';
import type { SyntheticMotionPayload } from '../types/syntheticMotionPayload';

export type { SyntheticMotionPayload } from '../types/syntheticMotionPayload';


export function SyntheticMotionDiagnostics({ payload }: { payload: SyntheticMotionPayload | null }) {
  const [error, setError] = useState<string | null>(null);
  const [selectedFrame, setSelectedFrame] = useState<number | null>(null);
  const requestDemo = () => {
    setError(null);
    socketService.requestSyntheticMotionDemo().catch((reason: unknown) => {
      setError(reason instanceof Error ? reason.message : 'Synthetic demo failed');
    });
  };
  const valid = payload?.schema_version === 1 &&
    payload.kind === 'synthetic_image_space_motion' &&
    payload.physical_contact_confirmed === false &&
    payload.impact_frame_index === null &&
    payload.impact_x_mm === null &&
    payload.impact_y_mm === null &&
    payload.position_uncertainty_mm === null;
  if (!valid || !payload) {
    return (
      <section className="impact-controls" aria-label="Synthetic motion diagnostics">
        <strong>SYNTHETIC MOTION · NOT MEASURED</strong>
        <p>Awaiting offline synthetic camera analysis. No physical impact detected.</p>
        <button type="button" onClick={requestDemo}>Load synthetic motion demo</button>
        {error && <p role="alert">{error}</p>}
      </section>
    );
  }
  const samples = payload.proximity_samples.filter((sample) =>
    Number.isFinite(sample.separation_px) && sample.separation_px >= 0
  );
  const max = Math.max(1, ...samples.map((sample) => sample.separation_px));
  const selected = samples.find((sample) => sample.frame_index === selectedFrame) ??
    samples.find((sample) => sample.frame_index === payload.closest_observed_frame_index) ??
    samples[0];
  const points = samples.map((sample, index) =>
    `${20 + index * (260 / Math.max(1, samples.length - 1))},${120 - (sample.separation_px / max) * 100}`
  ).join(' ');
  return (
    <section className="impact-controls" aria-label="Synthetic motion diagnostics">
      <strong>SYNTHETIC MOTION · PIXELS ONLY · NOT PHYSICAL CONTACT</strong>
      <button type="button" onClick={requestDemo}>Reload synthetic motion demo</button>
      {error && <p role="alert">{error}</p>}
      <p>{payload.motion_reason}</p>
      <p>Closest observed frame: {payload.closest_observed_frame_index ?? 'not established'}</p>
      <p>Approach and separation: {payload.has_observed_approach_and_separation ? 'observed' : 'not established'}</p>
      <svg viewBox="0 0 300 140" role="img" aria-label="Synthetic image-space separation by frame" style={{ width: '100%', maxWidth: 440 }}>
        <line x1="20" y1="120" x2="280" y2="120" stroke="currentColor" />
        <line x1="20" y1="20" x2="20" y2="120" stroke="currentColor" />
        {samples.length > 1 && <polyline points={points} fill="none" stroke="#79c5d4" strokeWidth="2" />}
        {samples.map((sample, index) => (
          <circle key={sample.frame_index} cx={20 + index * (260 / Math.max(1, samples.length - 1))}
            cy={120 - (sample.separation_px / max) * 100} r="3" fill="#79c5d4">
            <title>{`Frame ${sample.frame_index}: ${sample.separation_px.toFixed(2)} px`}</title>
          </circle>
        ))}
        <text x="150" y="137" textAnchor="middle" fontSize="9" fill="currentColor">Frame order · separation in pixels</text>
      </svg>
      <div role="group" aria-label="Select observed frame" style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
        {samples.map((sample) => (
          <button key={sample.frame_index} type="button"
            aria-pressed={selected?.frame_index === sample.frame_index}
            onClick={() => setSelectedFrame(sample.frame_index)}>
            Frame {sample.frame_index + 1}
          </button>
        ))}
      </div>
      {selected && (
        <p aria-live="polite">Selected frame {selected.frame_index + 1} · Separation {selected.separation_px.toFixed(2)} px · Sensor timestamp {selected.sensor_timestamp_ns} ns</p>
      )}
      <p>Rejected frames: {payload.rejected_frames.length}. Physical impact and accuracy remain unverified.</p>
    </section>
  );
}
