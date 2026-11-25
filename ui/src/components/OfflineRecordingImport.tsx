import { useId, useState } from 'react';
import { getServerOrigin } from '../utils/serverOrigin';

type Recording = {
  zip_sha: string;
  case: string;
  app_sha: string;
  capture_fingerprint: string;
  session_id: string;
  shot_id: string;
  timing_source: string;
  camera_identity: string;
  camera_mode_id: string;
  binding: { calibration_revision: string; club_model_id: string; club_geometry_revision: string };
};

async function recordingRequest(path = '', init?: RequestInit) {
  const response = await fetch(`${getServerOrigin()}/api/face-impact/recordings${path}`, {
    ...init,
    headers: { 'X-OpenFlight-Recording': '1', ...init?.headers },
  });
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new Error(data?.error ?? 'Recording operation unavailable');
  }
  return response;
}

export function OfflineRecordingImport({
  connected,
  onSaved,
}: {
  connected: boolean;
  onSaved: (sessionId: string) => Promise<void>;
}) {
  const id = useId();
  const [file, setFile] = useState<File | null>(null);
  const [items, setItems] = useState<Recording[]>([]);
  const [confirmRemoval, setConfirmRemoval] = useState(false);
  const [selected, setSelected] = useState('');
  const [fixtureCase, setFixtureCase] = useState('contact');
  const [pending, setPending] = useState(false);
  const [error, setError] = useState('');
  const [status, setStatus] = useState('');
  const recording = items.find((item) => item.zip_sha === selected);
  const disabled = !connected || pending;

  async function run(action: () => Promise<void>) {
    setPending(true);
    setError('');
    setStatus('');
    try {
      await action();
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'Recording operation failed');
    } finally {
      setPending(false);
    }
  }

  async function refresh() {
    const { recordings } = await (await recordingRequest()).json();
    setItems(recordings);
    setSelected((current) => current || recordings[0]?.zip_sha || '');
  }

  function fixture() {
    return run(async () => {
      const { digest } = await (
        await recordingRequest('/fixtures', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ case: fixtureCase }),
        })
      ).json();
      const data = await (await recordingRequest(`/${digest}`)).blob();
      const link = document.createElement('a');
      link.href = URL.createObjectURL(data);
      link.download = `face-impact-${fixtureCase}.zip`;
      link.click();
      window.setTimeout(() => URL.revokeObjectURL(link.href), 1000);
      setStatus('Synthetic ZIP downloaded. Select it below to import.');
    });
  }

  function importFile() {
    if (!file) return;
    return run(async () => {
      const { recording: imported } = await (await recordingRequest('', { method: 'POST', body: file })).json();
      await refresh();
      setSelected(imported.zip_sha);
      setStatus('ZIP matches its independent synthetic receipt. Ready for replay.');
    });
  }

  function replay() {
    return run(async () => {
      const { result } = await (
        await recordingRequest('/replay', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ digest: selected }),
        })
      ).json();
      if (result.accepted) {
        await onSaved(result.session_id);
        setStatus('Synthetic replay accepted and saved to session history.');
      } else {
        setStatus(`Synthetic replay rejected: ${result.reason}`);
      }
    });
  }

  return (
    <details
      aria-label="Recorded synthetic captures"
      onToggle={(event) => {
        if (event.currentTarget.open && connected) void run(refresh);
      }}
    >
      <summary>Import and replay recordings</summary>
      <div className="impact-controls__fields">
        <label>
          Sample recording
          <select value={fixtureCase} disabled={disabled} onChange={(event) => setFixtureCase(event.target.value)}>
            <option value="contact">Contact</option>
            <option value="heel-contact">Heel contact</option>
            <option value="compact-contact">Compact club</option>
            <option value="missing-markers">Missing landmarks</option>
            <option value="ambiguous-contact">Ambiguous contact</option>
          </select>
        </label>
        <button type="button" disabled={disabled} onClick={() => void fixture()}>
          Download synthetic sample
        </button>
        <label htmlFor={id}>Recording ZIP</label>
        <input
          id={id}
          type="file"
          accept=".zip,application/zip"
          disabled={disabled}
          onChange={(event) => setFile(event.target.files?.[0] ?? null)}
        />
        <button type="button" disabled={disabled || !file} onClick={() => void importFile()}>
          Import recording
        </button>
        <label>
          Imported recording
          <select
            value={selected}
            disabled={disabled}
            onChange={(event) => {
              setSelected(event.target.value);
              setConfirmRemoval(false);
            }}
          >
            <option value="">Select a recording</option>
            {items.map((item) => (
              <option key={item.zip_sha} value={item.zip_sha}>
                {item.case} · {item.zip_sha.slice(0, 12)}
              </option>
            ))}
          </select>
        </label>
        <button type="button" disabled={disabled} onClick={() => void run(refresh)}>
          Refresh recordings
        </button>
        <button type="button" disabled={disabled || !recording} onClick={() => void replay()}>
          Replay recording
        </button>
      </div>
      {recording && (
        <div className="impact-controls__fields">
          {confirmRemoval ? (
            <>
              <button
                disabled={disabled}
                onClick={() =>
                  void run(async () => {
                    await recordingRequest('/remove-import', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({ digest: selected }),
                    });
                    setSelected('');
                    setConfirmRemoval(false);
                    await refresh();
                    setStatus('Imported ZIP removed. Receipt and session history retained.');
                  })
                }
              >
                Confirm remove imported ZIP
              </button>
              <button onClick={() => setConfirmRemoval(false)}>Cancel</button>
            </>
          ) : (
            <button disabled={disabled} onClick={() => setConfirmRemoval(true)}>
              Remove imported ZIP
            </button>
          )}
        </div>
      )}
      {recording && (
        <dl aria-label="Recording revisions" style={{ overflowWrap: 'anywhere' }}>
          <dt>Status</dt>
          <dd>Independent synthetic receipt matched</dd>
          <dt>Session and shot</dt>
          <dd>
            {recording.session_id} · {recording.shot_id}
          </dd>
          <dt>Capture fingerprint</dt>
          <dd>{recording.capture_fingerprint}</dd>
          <dt>Camera and mode</dt>
          <dd>
            {recording.camera_identity} · {recording.camera_mode_id}
          </dd>
          <dt>Optics revision</dt>
          <dd>{recording.binding.calibration_revision}</dd>
          <dt>Club and geometry revision</dt>
          <dd>
            {recording.binding.club_model_id} · {recording.binding.club_geometry_revision}
          </dd>
          <dt>Timing and software</dt>
          <dd>
            {recording.timing_source} · {recording.app_sha}
          </dd>
        </dl>
      )}
      {pending && <p role="status">Working with recording…</p>}
      {status && <p role="status">{status}</p>}
      {error && <p role="alert">{error}</p>}
    </details>
  );
}
