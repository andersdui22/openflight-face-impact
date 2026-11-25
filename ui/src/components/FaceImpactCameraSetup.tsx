import { useState } from 'react';
import { getServerOrigin } from '../utils/serverOrigin';

const fixture = 'fixture:camera-setup-v1';
const storageKey = 'openflight.face-impact.camera-identity';
type Device = { identity: string; name: string; status: string };

export interface CameraDiagnostics {
  requested?: { width: number; height: number; requested_fps: number } | null;
  negotiated?: { width: number | null; height: number | null; reported_fps: number | null } | null;
  delivered_size?: [number, number] | null;
  delivered_fps?: number | null;
  last_frame_age_ms?: number | null;
  frames_received?: number;
  timestamp_source?: string;
  driver_controls?: Record<string, { accepted_by_driver: boolean; reported: number | null }>;
}

async function setupRequest(action: string, data: object = {}) {
  const response = await fetch(`${getServerOrigin()}/api/face-impact/camera-setup/${action}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-OpenFlight-Camera-Setup': '1' },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    const error = await response.json().catch(() => null);
    throw new Error(error?.error ?? 'Camera setup unavailable');
  }
  return response;
}

export function FaceImpactCameraSetup({ diagnostics }: { diagnostics: CameraDiagnostics | null }) {
  const [devices, setDevices] = useState<Device[]>([]);
  const [identity, setIdentity] = useState(() =>
    typeof window === 'undefined' ? fixture : (window.localStorage.getItem(storageKey) ?? fixture)
  );
  const [resolution, setResolution] = useState('320x200');
  const [fps, setFps] = useState('30');
  const [exposure, setExposure] = useState('');
  const [gain, setGain] = useState('');
  const [profile, setProfile] = useState<File | null>(null);
  const [clubEvidence, setClubEvidence] = useState<File | null>(null);
  const [revision, setRevision] = useState('');
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const discovered = devices.some((device) => device.identity === identity);
  const finite = (value?: number | null) => (value == null ? 'Unknown' : value.toFixed(1));

  async function run(action: () => Promise<void>) {
    setBusy(true);
    setError('');
    setStatus('');
    try {
      await action();
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'Camera setup failed');
    } finally {
      setBusy(false);
    }
  }

  return (
    <details className="impact-controls" aria-label="Face Impact camera setup">
      <summary>Camera setup and diagnostics</summary>
      <div className="impact-controls__fields">
        <button
          disabled={busy}
          onClick={() =>
            void run(async () => {
              const payload = await (await setupRequest('inventory')).json();
              setDevices(payload.devices);
              setStatus(`${payload.devices.length} Windows camera device(s) found.`);
            })
          }
        >
          Scan Windows cameras
        </button>
        <label>
          Camera identity
          <select
            value={identity}
            onChange={(event) => {
              setIdentity(event.target.value);
              localStorage.setItem(storageKey, event.target.value);
            }}
          >
            <option value={fixture}>Diagnostic fixture</option>
            {identity !== fixture && !discovered && <option value={identity}>Saved device · unavailable</option>}
            {devices.map((device) => (
              <option key={device.identity} value={device.identity}>
                {device.name} · {device.status}
              </option>
            ))}
          </select>
        </label>
        {identity !== fixture && <p>Windows device identity: {identity}. Capture association is unverified.</p>}
        <label>
          Requested resolution{' '}
          <select value={resolution} onChange={(event) => setResolution(event.target.value)}>
            <option>320x200</option>
            <option>640x400</option>
          </select>
        </label>
        <label>
          Requested FPS{' '}
          <select value={fps} onChange={(event) => setFps(event.target.value)}>
            <option>30</option>
            <option>60</option>
            <option>120</option>
          </select>
        </label>
        <label>
          Exposure (driver units){' '}
          <input type="number" value={exposure} onChange={(event) => setExposure(event.target.value)} />
        </label>
        <label>
          Gain (driver units) <input type="number" value={gain} onChange={(event) => setGain(event.target.value)} />
        </label>
        <button
          disabled={busy || identity !== fixture}
          onClick={() =>
            void run(async () => {
              const [width, height] = resolution.split('x').map(Number);
              await setupRequest('start', {
                identity,
                width,
                height,
                fps: Number(fps),
                exposure: exposure === '' ? null : Number(exposure),
                gain: gain === '' ? null : Number(gain),
              });
              setStatus('Diagnostic fixture started or reconnected.');
            })
          }
        >
          Start or reconnect fixture
        </button>
        <button
          disabled={busy}
          onClick={() =>
            void run(async () => {
              await setupRequest('stop');
              setStatus('Diagnostic fixture stopped.');
            })
          }
        >
          Stop fixture
        </button>
        <button
          disabled={busy || identity !== fixture || !diagnostics?.delivered_size}
          onClick={() =>
            void run(async () => {
              const blob = await (await setupRequest('record')).blob();
              const url = URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.download = 'face-impact-diagnostic.zip';
              link.click();
              window.setTimeout(() => URL.revokeObjectURL(url), 1000);
              setStatus('Diagnostic capture exported with host timing. Physical measurement unavailable.');
            })
          }
        >
          Record and export diagnostic
        </button>
      </div>
      <dl>
        <dt>Requested mode</dt>
        <dd>
          {diagnostics?.requested
            ? `${diagnostics.requested.width} × ${diagnostics.requested.height} @ ${diagnostics.requested.requested_fps} FPS`
            : 'Unknown'}
        </dd>
        <dt>Driver-reported mode</dt>
        <dd>
          {diagnostics?.negotiated
            ? `${diagnostics.negotiated.width ?? '?'} × ${diagnostics.negotiated.height ?? '?'} @ ${finite(diagnostics.negotiated.reported_fps)} FPS`
            : 'Unknown'}
        </dd>
        <dt>Delivered dimensions</dt>
        <dd>{diagnostics?.delivered_size?.join(' × ') ?? 'Unknown'}</dd>
        <dt>Observed delivery FPS / frame age (ms)</dt>
        <dd>
          {finite(diagnostics?.delivered_fps)} / {finite(diagnostics?.last_frame_age_ms)}
        </dd>
        <dt>Received frames / dropped frames</dt>
        <dd>{diagnostics?.frames_received ?? 'Unknown'} / Unknown</dd>
        <dt>Timing quality</dt>
        <dd>
          {diagnostics?.timestamp_source ? 'Host arrival only · independent exposure timing unavailable' : 'Unknown'}
        </dd>
        <dt>Reported exposure / gain</dt>
        <dd>
          {finite(diagnostics?.driver_controls?.exposure?.reported)} /{' '}
          {finite(diagnostics?.driver_controls?.gain?.reported)}
        </dd>
      </dl>
      <div className="impact-controls__fields">
        <label>
          Offline optics profile{' '}
          <input
            type="file"
            accept=".json,application/json"
            onChange={(event) => setProfile(event.target.files?.[0] ?? null)}
          />
        </label>
        <label>
          Offline club and binding JSON
          <input
            type="file"
            accept=".json,application/json"
            onChange={(event) => setClubEvidence(event.target.files?.[0] ?? null)}
          />
        </label>
        <label>
          Expected profile revision <input value={revision} onChange={(event) => setRevision(event.target.value)} />
        </label>
        <button
          disabled={busy || !profile}
          onClick={() =>
            void run(async () => {
              if (!profile || profile.size + (clubEvidence?.size ?? 0) > 64 * 1024)
                throw new Error('Choose offline profile and binding files up to 64 KiB combined');
              const result = await (
                await setupRequest('profile', {
                  profile: await profile.text(),
                  expected_revision: revision,
                  club_evidence: await clubEvidence?.text(),
                })
              ).json();
              setStatus(
                `Offline calibration: ${result.status.state} · ${result.profile_revision} · Club binding: ${result.club_binding_status}`
              );
            })
          }
        >
          Inspect optics profile
        </button>
      </div>
      {status && (
        <p role="status" style={{ overflowWrap: 'anywhere' }}>
          {status}
        </p>
      )}
      {error && <p role="alert">{error}</p>}
    </details>
  );
}
