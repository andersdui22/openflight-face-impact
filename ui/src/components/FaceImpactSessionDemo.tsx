export type DemoShot = { id: number; x: number; y: number };
const points = [
  { x: -12, y: 8 },
  { x: 7, y: -5 },
  { x: 2, y: 3 },
  { x: -5, y: -2 },
  { x: 11, y: 6 },
];

export function FaceImpactSessionDemo({ enabled, setEnabled, shots, setShots }: {
  enabled: boolean;
  setEnabled: (enabled: boolean) => void;
  shots: DemoShot[];
  setShots: (update: (current: DemoShot[]) => DemoShot[]) => void;
}) {
  const average = (axis: 'x' | 'y') =>
    shots.length ? (shots.reduce((sum, shot) => sum + shot[axis], 0) / shots.length).toFixed(1) : '—';

  return (
    <section className="impact-controls" aria-label="Face Impact simulated session">
      <strong>SIMULATED SESSION — DEMO ONLY</strong>
      <p>Sample coordinates in mm. Not camera measurements or recorded shots.</p>
      <div className="impact-controls__fields">
        <button type="button" aria-pressed={enabled} onClick={() => {
            if (enabled) setShots(() => []);
            setEnabled(!enabled);
          }}>
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
        <button type="button" disabled={!enabled || shots.length === 0} onClick={() => setShots(() => [])}>
          RESET DEMO SESSION
        </button>
      </div>
      {enabled && (
        <div aria-label="Simulated session statistics">
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
