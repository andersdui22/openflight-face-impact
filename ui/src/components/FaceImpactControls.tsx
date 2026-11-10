import { useState } from 'react';

type VisualTab = 'setup' | 'calibration' | 'capture' | 'replay';

const tabs: { id: VisualTab; title: string }[] = [
  { id: 'setup', title: 'Camera setup' },
  { id: 'calibration', title: 'Calibration' },
  { id: 'capture', title: 'Capture' },
  { id: 'replay', title: 'Replay' },
];

export function FaceImpactControls() {
  const [tab, setTab] = useState<VisualTab>('setup');
  const [handedness, setHandedness] = useState('right');
  const [cameraPosition, setCameraPosition] = useState('face-on');
  const [overlay, setOverlay] = useState(true);

  return (
    <section className="impact-controls" aria-label="Face Impact controls">
      <div className="impact-controls__tabs" role="group" aria-label="Configuration sections">
        {tabs.map((item) => (
          <button
            key={item.id}
            type="button"
            aria-pressed={tab === item.id}
            onClick={() => setTab(item.id)}
          >
            {item.title}
          </button>
        ))}
      </div>
      <div className="impact-controls__fields">
        {tab === 'setup' ? (
          <>
            <label>
              Camera model
              <input value="ELP OV9281 USB" readOnly aria-label="Camera model" />
            </label>
            <label>
              Handedness
              <select value={handedness} onChange={(event) => setHandedness(event.target.value)}>
                <option value="right">Right-handed</option>
                <option value="left">Left-handed</option>
              </select>
            </label>
            <label>
              Camera position
              <select value={cameraPosition} onChange={(event) => setCameraPosition(event.target.value)}>
                <option value="face-on">Face-on</option>
                <option value="side">Side</option>
                <option value="top">Top</option>
              </select>
            </label>
            <label className="impact-controls__checkbox">
              <input type="checkbox" checked={overlay} onChange={(event) => setOverlay(event.target.checked)} />
              Show alignment overlay (preview only)
            </label>
            <button type="button" disabled title="Camera integration is not available in Gate 07">
              CONNECT CAMERA — NOT AVAILABLE
            </button>
          </>
        ) : tab === 'calibration' ? (
          <>
            <span>Calibration status: NOT CALIBRATED</span>
            <span>Marker detection: NOT AVAILABLE</span>
            <button type="button" disabled title="Calibration requires approved camera integration">
              START CALIBRATION — NOT AVAILABLE
            </button>
            <button type="button" disabled title="Calibration requires validated observations">
              SAVE CALIBRATION — NOT AVAILABLE
            </button>
          </>
        ) : tab === 'capture' ? (
          <>
            <span>Capture status: OFFLINE</span>
            <span>Measured impact: NO DATA</span>
            <button type="button" disabled title="Shot capture is not implemented">
              START CAPTURE — NOT AVAILABLE
            </button>
            <button type="button" disabled title="Shot capture is not implemented">
              STOP CAPTURE — NOT AVAILABLE
            </button>
          </>
        ) : (
          <>
            <span>Recorded shots: NO CAPTURES</span>
            <button type="button" disabled title="No validated shot recording exists">
              PLAY — NOT AVAILABLE
            </button>
            <button type="button" disabled title="No validated shot recording exists">
              FRAME STEP — NOT AVAILABLE
            </button>
            <button type="button" disabled title="No validated shot recording exists">
              EXPORT — NOT AVAILABLE
            </button>
          </>
        )}
      </div>
      <p className="impact-controls__disclaimer">
        UI preview only. Settings are local to this view and are not saved. No camera measurements are active.
      </p>
    </section>
  );
}
