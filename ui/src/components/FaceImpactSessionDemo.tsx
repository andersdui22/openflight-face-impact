import { useState } from 'react';

type DemoShot = { id: number; x: number; y: number };
const points = [
  { x: -12, y: 8 },
  { x: 7, y: -5 },
  { x: 2, y: 3 },
  { x: -5, y: -2 },
  { x: 11, y: 6 },
];

export function FaceImpactSessionDemo() {
  const [enabled, setEnabled] = useState(false);
  const [shots, setShots] = useState<DemoShot[]>([]);
  const average = (axis: 'x' | 'y') =>
    shots.length ? (shots.reduce((sum, shot) => sum + shot[axis], 0) / shots.length).toFixed(1) : '—';

  return (
    <section className="impact-controls" aria-label="Face Impact simulated session">
      <strong>SIMULATED SESSION — DEMO ONLY</strong>
      <p>Sample coordinates in mm. Not camera measurements or recorded shots.</p>
      <div className="impact-controls__fields">
        <button type="button" aria-pressed={enabled} onClick={() => setEnabled((value) => !value)}>
          {enabled ? 'EXIT DEMO MODE' : 'ENTER DEMO MODE'}
        </button>
        <button
          type="button"
          disabled={!enabled}
          onClick={() =>
            setShots((current) => {
              const point = points[current.length % points.length];
              return [...current, { id: current.length + 1, ...point }];
            })
          }
        >
          ADD SIMULATED SHOT
        </button>
        <button type="button" disabled={!enabled || shots.length === 0} onClick={() => setShots([])}>
          RESET DEMO SESSION
        </button>
      </div>
      {enabled && (
        <div aria-label="Simulated session statistics">
          <div aria-label="Simulated impact distribution" style={{ maxWidth: 300, margin: '12px 0' }}>
            <svg viewBox="0 0 300 180" role="img" aria-label={`DEMO ONLY impact map with ${shots.length} simulated shots`} style={{ width: '100%', background: '#15243a', border: '1px solid #607d9a' }}>
              <rect x="30" y="20" width="240" height="140" rx="28" fill="#243b53" stroke="#8eb3cf" strokeWidth="2" />
              <line x1="150" y1="20" x2="150" y2="160" stroke="#6987a1" strokeDasharray="4 4" />
              <line x1="30" y1="90" x2="270" y2="90" stroke="#6987a1" strokeDasharray="4 4" />
              {shots.map((shot) => (
                <circle key={shot.id} cx={150 + shot.x * 4} cy={90 - shot.y * 4} r="6" fill="#79c5d4" stroke="#ffffff" strokeWidth="1.5">
                  <title>{`SIMULATED SHOT ${shot.id}: X ${shot.x} mm, Y ${shot.y} mm`}</title>
                </circle>
              ))}
              <text x="150" y="14" textAnchor="middle" fontSize="10" fill="#e5f4ff">SIMULATED IMPACT MAP · DEMO ONLY</text>
            </svg>
          </div>
          <p role="status">
            SIMULATED SHOTS: {shots.length} · AVERAGE X: {average('x')} mm · AVERAGE Y: {average('y')} mm
          </p>
          <ol aria-label="Simulated shot history">
            {shots.map((shot) => (
              <li key={shot.id}>
                SIMULATED SHOT {shot.id}: X {shot.x} mm, Y {shot.y} mm
              </li>
            ))}
          </ol>
        </div>
      )}
    </section>
  );
}
