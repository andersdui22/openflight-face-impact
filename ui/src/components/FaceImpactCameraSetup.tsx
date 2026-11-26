import { useState } from 'react';
import { getServerOrigin } from '../utils/serverOrigin';

const fixture = 'fixture:camera-setup-v1';
const storageKey = 'openflight.face-impact.camera-identity';
type Mode = {
  width: number;
  height: number;
  numerator: number;
  denominator: number;
  format: number;
  pixel_format: string;
};
const fpsLabel = new Intl.NumberFormat('en-US', { maximumFractionDigits: 1, useGrouping: false });

function modeKey(mode: Mode) {
  return [mode.width, mode.height, mode.numerator, mode.denominator, mode.format].join(':');
}

type Device = { identity: string; name: string; status: string };

type IntervalStats = { min: number; max: number; median: number; stddev: number; p95: number; p99: number };
type ControlRange = {
  minimum: number;
  maximum: number;
  step: number;
  default: number;
  supports_auto: boolean;
  supports_manual: boolean;
};

export interface CameraDiagnostics {
  last_error?: string | null;
  requested?: { width: number; height: number; requested_fps: number } | null;
  negotiated?: { width: number | null; height: number | null; reported_fps: number | null } | null;
  delivered_size?: [number, number] | null;
  delivered_fps?: number | null;
  last_frame_age_ms?: number | null;
  frames_received?: number;
  timestamp_source?: string;
  identity?: { selected: string | null; opened: string | null; status: string; backend: string } | null;
  host_frame_intervals_ms?: { count: number; min: number; max: number; mean: number; stddev: number } | null;
  sample_timestamp_source?: string | null;
  native_mode?: Mode | null;
  exposure_mode?: { requested_mode: string; reported_mode: string | null } | null;
  latest_driver_sample?: {
    sample_time_100ns: number | null;
    sample_duration_100ns: number | null;
    discontinuity: boolean;
    sequence: number | null;
  } | null;
  sensor_timestamp_available?: boolean;
  driver_controls?: Record<
    string,
    { requested: number | null; accepted_by_driver: boolean | null; reported: number | null }
  >;
  driver_ranges?: Record<string, ControlRange | null> | null;
  capture_diagnostics?: {
    timing: Record<string, IntervalStats | number | null>;
    buffer: {
      history_frames: number;
      history_capacity: number;
      capture_capacity: number | null;
      history_evictions: number;
    };
    preview: { encodes: number; encode_wall_ms: number };
    processed_frames: number;
    received_frames: number | null;
  } | null;
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
  const [modes, setModes] = useState<Mode[]>([]);
  const [nativeMode, setNativeMode] = useState('');
  const [activatePhysical, setActivatePhysical] = useState(false);
  const [exposureMode, setExposureMode] = useState('unchanged');
  const physicalSelected = identity !== fixture;
  const physicalRunning =
    diagnostics?.identity?.backend === 'media_foundation' && diagnostics.identity.status === 'handle_match';
  const [resolution, setResolution] = useState('320x200');
  const [fps, setFps] = useState('30');
  const [windowUnit, setWindowUnit] = useState('frames');
  const [preFrames, setPreFrames] = useState('3');
  const [postFrames, setPostFrames] = useState('3');
  const [purpose, setPurpose] = useState('diagnostic');
  const [exposure, setExposure] = useState('');
  const [gain, setGain] = useState('');
  const [profile, setProfile] = useState<File | null>(null);
  const [clubEvidence, setClubEvidence] = useState<File | null>(null);
  const [revision, setRevision] = useState('');
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState('');
  const [exportedFrames, setExportedFrames] = useState<string | null>(null);
  const [error, setError] = useState('');
  const selectedMode = modes.find((mode) => modeKey(mode) === nativeMode);
  const discovered = devices.some((device) => device.identity === identity);
  const capture = diagnostics?.capture_diagnostics;
  const ranges = physicalRunning ? diagnostics?.driver_ranges : null;
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
            disabled={busy}
            onChange={(event) => {
              setIdentity(event.target.value);
              setModes([]);
              setNativeMode('');
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
        {identity !== fixture && (
          <p>Windows device identity: {identity}. Physical capture requires an exact handle match.</p>
        )}
        {physicalSelected ? (
          <>
            <button
              disabled={busy || !discovered || physicalRunning || !activatePhysical}
              onClick={() =>
                void run(async () => {
                  const response = await (await setupRequest('modes', { identity, activate_physical: true })).json();
                  const advertised: Mode[] = response.modes;
                  const nextMode =
                    advertised.find((mode) => modeKey(mode) === nativeMode) ??
                    (modes.length ? undefined : advertised[0]);
                  setModes(advertised);
                  setNativeMode(nextMode ? modeKey(nextMode) : '');
                  setStatus(
                    response.modes.length ? 'Advertised native modes loaded.' : 'No supported native mode advertised.'
                  );
                })
              }
            >
              Load advertised modes
            </button>
            <label>
              Advertised camera mode
              <select value={nativeMode} disabled={busy} onChange={(event) => setNativeMode(event.target.value)}>
                <option value="">Select a native mode</option>
                {modes.map((mode) => (
                  <option key={modeKey(mode)} value={modeKey(mode)} title={`${mode.numerator}/${mode.denominator} FPS`}>
                    {mode.width} × {mode.height} · {fpsLabel.format(mode.numerator / mode.denominator)} FPS ·{' '}
                    {mode.pixel_format}
                  </option>
                ))}
              </select>
            </label>
            <label>
              Exposure mode{' '}
              <select value={exposureMode} onChange={(event) => setExposureMode(event.target.value)}>
                <option value="unchanged">Driver default</option>
                <option value="auto">Auto</option>
                <option value="manual">Manual</option>
              </select>
            </label>
            <label>
              <input
                type="checkbox"
                checked={activatePhysical}
                onChange={(event) => setActivatePhysical(event.target.checked)}
              />{' '}
              Enable physical diagnostics
            </label>
          </>
        ) : (
          <>
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
          </>
        )}
        <label>
          Exposure (driver units){' '}
          <input
            type="number"
            min={ranges?.exposure?.minimum}
            max={ranges?.exposure?.maximum}
            step={ranges?.exposure?.step || 1}
            value={exposure}
            onChange={(event) => setExposure(event.target.value)}
          />
        </label>
        <label>
          Gain (driver units){' '}
          <input
            type="number"
            min={ranges?.gain?.minimum}
            max={ranges?.gain?.maximum}
            step={ranges?.gain?.step || 1}
            value={gain}
            onChange={(event) => setGain(event.target.value)}
          />
        </label>
        <button
          disabled={busy || (physicalSelected && (!discovered || !activatePhysical || !selectedMode))}
          onClick={() =>
            void run(async () => {
              const [width, height] = resolution.split('x').map(Number);
              await setupRequest('start', {
                identity,
                activate_physical: physicalSelected && activatePhysical,
                mode: physicalSelected ? selectedMode : undefined,
                exposure_mode: exposureMode,
                width,
                height,
                fps: Number(fps),
                exposure: exposure === '' ? null : Number(exposure),
                gain: gain === '' ? null : Number(gain),
              });
              setStatus(
                physicalSelected
                  ? 'Physical diagnostic capture started or reconnected.'
                  : 'Diagnostic fixture started or reconnected.'
              );
            })
          }
        >
          {physicalSelected ? 'Start or reconnect physical camera' : 'Start or reconnect fixture'}
        </button>
        <button
          disabled={busy}
          onClick={() =>
            void run(async () => {
              await setupRequest('stop');
              setStatus('Camera capture stopped.');
            })
          }
        >
          {physicalSelected ? 'Stop physical camera' : 'Stop fixture'}
        </button>
        <label>
          Recording window units
          <select value={windowUnit} onChange={(event) => setWindowUnit(event.target.value)}>
            <option value="frames">Frames</option>
            <option value="ms">Milliseconds (nominal)</option>
          </select>
        </label>
        <label>
          {windowUnit === 'frames' ? 'Frames before trigger' : 'Milliseconds before trigger'}
          <input
            type="number"
            min="1"
            max={windowUnit === 'frames' ? (capture?.buffer.capture_capacity ?? 512) - 1 : 20000}
            value={preFrames}
            onChange={(event) => setPreFrames(event.target.value)}
          />
        </label>
        <label>
          {windowUnit === 'frames' ? 'Frames after trigger' : 'Milliseconds after trigger'}
          <input
            type="number"
            min="1"
            max={windowUnit === 'frames' ? (capture?.buffer.capture_capacity ?? 512) - 1 : 20000}
            value={postFrames}
            onChange={(event) => setPostFrames(event.target.value)}
          />
        </label>
        {capture?.buffer.capture_capacity != null && (
          <p>Recording limit for this mode: {capture.buffer.capture_capacity} total frames.</p>
        )}
        <label>
          Capture purpose
          <select value={purpose} onChange={(event) => setPurpose(event.target.value)}>
            <option value="diagnostic">General diagnostics</option>
            <option value="checkerboard">Checkerboard reference</option>
            <option value="club_landmarks">Club landmark reference</option>
            <option value="setup_reference">Camera setup reference</option>
            <option value="golf_diagnostic">Golf swing diagnostic</option>
          </select>
        </label>
        <button
          disabled={busy || !diagnostics?.delivered_size || (physicalSelected && !physicalRunning)}
          onClick={() =>
            void run(async () => {
              const windowSettings =
                windowUnit === 'frames'
                  ? { pre_frames: Number(preFrames), post_frames: Number(postFrames) }
                  : { pre_ms: Number(preFrames), post_ms: Number(postFrames) };
              const response = await setupRequest('record', { purpose, ...windowSettings });
              const blob = await response.blob();
              setExportedFrames(response.headers.get('X-OpenFlight-Exported-Frames'));
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
      <p>
        {physicalRunning
          ? 'Physical camera · diagnostic only'
          : diagnostics?.identity?.status === 'fixture_match'
            ? 'Diagnostic fixture'
            : 'Camera inactive'}
      </p>
      <dl>
        <dt>Capture backend / identity status</dt>
        <dd>
          {diagnostics?.identity
            ? `${diagnostics.identity.backend} · ${diagnostics.identity.status}`
            : 'Camera inactive'}
        </dd>
        <dt>Selected by capture / opened handle</dt>
        <dd>
          {diagnostics?.identity?.selected ?? 'Unknown'} / {diagnostics?.identity?.opened ?? 'Unknown'}
        </dd>
        <dt>Host interval mean / variation (ms)</dt>
        <dd>
          {finite(diagnostics?.host_frame_intervals_ms?.mean)} / {finite(diagnostics?.host_frame_intervals_ms?.stddev)}
        </dd>
        <dt>Driver sample timestamp source / sensor time</dt>
        <dd>
          {diagnostics?.sample_timestamp_source ?? 'Unavailable'} /{' '}
          {diagnostics?.sensor_timestamp_available ? 'Available' : 'Unknown'}
        </dd>
        <dt>Negotiated native pixel format / exposure mode</dt>
        <dd>
          {diagnostics?.native_mode?.pixel_format ?? 'Unknown'} /{' '}
          {diagnostics?.exposure_mode?.reported_mode ?? 'Unknown'}
        </dd>
        <dt>Driver sample time / duration (100 ns)</dt>
        <dd>
          {diagnostics?.latest_driver_sample?.sample_time_100ns ?? 'Unknown'} /{' '}
          {diagnostics?.latest_driver_sample?.sample_duration_100ns ?? 'Unknown'}
        </dd>
        <dt>Driver discontinuity / sequence</dt>
        <dd>
          {diagnostics?.latest_driver_sample ? String(diagnostics.latest_driver_sample.discontinuity) : 'Unknown'} /{' '}
          {diagnostics?.latest_driver_sample?.sequence ?? 'Unknown'}
        </dd>
        <dt>Selected native frame rate</dt>
        <dd>
          {selectedMode
            ? `${selectedMode.numerator}/${selectedMode.denominator} FPS · ${selectedMode.pixel_format}`
            : 'Unknown'}
        </dd>
        <dt>Requested mode</dt>
        <dd>
          {diagnostics?.requested
            ? `${diagnostics.requested.width} × ${diagnostics.requested.height} @ ${fpsLabel.format(diagnostics.requested.requested_fps)} FPS`
            : 'Unknown'}
        </dd>
        <dt>Driver-reported mode</dt>
        <dd>
          {diagnostics?.negotiated
            ? `${diagnostics.negotiated.width ?? '?'} × ${diagnostics.negotiated.height ?? '?'} @ ${finite(diagnostics.negotiated.reported_fps)} FPS`
            : 'Unknown'}
        </dd>
        {diagnostics?.last_error && (
          <>
            <dt>Capture error</dt>
            <dd>{diagnostics.last_error}</dd>
          </>
        )}
        <dt>Delivered dimensions</dt>
        <dd>{diagnostics?.delivered_size?.join(' × ') ?? 'Unknown'}</dd>
        <dt>Observed delivery FPS / frame age (ms)</dt>
        <dd>
          {finite(diagnostics?.delivered_fps)} / {finite(diagnostics?.last_frame_age_ms)}
        </dd>
        <dt>Received / processed / last exported frames</dt>
        <dd>
          {capture?.received_frames ?? 'Unknown'} /{' '}
          {capture?.processed_frames ?? diagnostics?.frames_received ?? 'Unknown'} / {exportedFrames ?? 'Unknown'}
        </dd>
        <dt>Buffer occupancy / history evictions</dt>
        <dd>
          {capture
            ? `${capture.buffer.history_frames}/${capture.buffer.history_capacity} · ${capture.buffer.history_evictions}`
            : 'Unknown'}
        </dd>
        <dt>Dropped frames / discontinuities / equal sample timestamps</dt>
        <dd>
          Unknown / {(capture?.timing.discontinuities as number) ?? 'Unknown'} /{' '}
          {(capture?.timing.adjacent_equal_sample_timestamps as number) ?? 'Unknown'}
        </dd>
        <dt>Preview JPEG encodes / elapsed encoding time (ms)</dt>
        <dd>
          {capture?.preview.encodes ?? 'Unknown'} / {finite(capture?.preview.encode_wall_ms)}
        </dd>
        {Object.entries({
          host_arrival_ms: 'Host arrival',
          sample_timestamp_ms: 'Driver sample',
          native_callback_ms: 'Native callback',
          sample_duration_ms: 'Driver sample duration',
          callback_to_readout_ms: 'Callback to native readout',
          python_processing_ms: 'Python raster preparation',
        }).map(([key, label]) => {
          const stats = capture?.timing[key];
          return (
            <div key={key}>
              <dt>{label} (ms), min / median / max / SD / P95 / P99</dt>
              <dd>
                {stats && typeof stats === 'object'
                  ? [stats.min, stats.median, stats.max, stats.stddev, stats.p95, stats.p99].map(finite).join(' / ')
                  : 'Unknown'}
              </dd>
            </div>
          );
        })}
        <dt>Timing quality</dt>
        <dd>
          {diagnostics?.timestamp_source ? 'Host arrival only · independent exposure timing unavailable' : 'Unknown'}
        </dd>
        {(['exposure', 'gain'] as const).map((name) => {
          const range = ranges?.[name];
          const control = diagnostics?.driver_controls?.[name];
          return (
            <div key={name}>
              <dt>{name} requested / driver accepted / readback (driver units)</dt>
              <dd>
                {control?.requested ?? 'Unknown'} /{' '}
                {control?.accepted_by_driver == null ? 'Unknown' : String(control.accepted_by_driver)} /{' '}
                {control?.reported ?? 'Unknown'}
              </dd>
              <dt>{name} range / step / auto / manual</dt>
              <dd>
                {range
                  ? `${range.minimum} to ${range.maximum} / ${range.step} / ${range.supports_auto} / ${range.supports_manual}`
                  : 'Unknown'}
              </dd>
            </div>
          );
        })}
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
