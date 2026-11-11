import { useEffect, useState } from 'react';
import { getServerOrigin } from '../utils/serverOrigin';

type CameraState = 'checking' | 'disabled' | 'starting' | 'running' | 'stopped' | 'error' | 'offline';

type CalibrationState =
  'not_calibrated' | 'mode_unknown' | 'mode_incompatible' | 'profile_invalid' | 'revision_invalid' | 'binding_incompatible' | 'evidence_invalid' | 'offline_profile_compatible';

interface CalibrationStatus {
  state: CalibrationState;
  physical_validation: false;
  evidence_kind: 'synthetic_offline' | null;
  fit_rms_px: number | null;
  validation_rms_px: number[] | null;
}

interface UsbStatus {
  enabled: boolean;
  state: 'disabled' | 'starting' | 'running' | 'stopped' | 'error';
  last_error?: string | null;
  calibration?: CalibrationStatus;
}

function calibrationLabel(status: CalibrationStatus | null): string {
  switch (status?.state) {
    case 'offline_profile_compatible':
      return 'Offline calibration profile compatible · physical validation not performed';
    case 'mode_incompatible':
      return 'Calibration profile incompatible with camera mode';
    case 'profile_invalid':
      return 'Calibration profile invalid or unreadable';
    case 'revision_invalid':
      return 'Calibration revision missing or stale · measurements disabled';
    case 'binding_incompatible':
      return 'Club model or calibration binding incompatible · measurements disabled';
    case 'evidence_invalid':
      return 'Calibration or club evidence invalid · measurements disabled';
    case 'mode_unknown':
      return 'Calibration profile loaded · camera mode not verified';
    default:
      return 'Camera not physically calibrated';
  }
}

function backendOrigin(): string {
  const origin = getServerOrigin();
  // Packaged Electron uses file:// and has no bundled Python backend.
  // An explicit loopback address avoids treating file:// as an HTTP API.
  return origin === 'null' || origin.startsWith('file:') ? 'http://127.0.0.1:8080' : origin;
}

export function FaceImpactCameraPreview() {
  const [state, setState] = useState<CameraState>('checking');
  const [error, setError] = useState<string | null>(null);
  const [previewFailed, setPreviewFailed] = useState(false);
  const [frameKey, setFrameKey] = useState(0);
  const [calibration, setCalibration] = useState<CalibrationStatus | null>(null);

  useEffect(() => {
    const controller = new AbortController();
    let mounted = true;
    let requestInFlight = false;
    const check = async () => {
      if (requestInFlight) {
        return;
      }
      requestInFlight = true;
      try {
        const response = await fetch(`${backendOrigin()}/api/camera/usb/status`, {
          signal: controller.signal,
          cache: 'no-store',
        });
        if (!response.ok) {
          throw new Error('Camera service unavailable');
        }
        const status = (await response.json()) as UsbStatus;
        if (!mounted) {
          return;
        }
        const nextState: CameraState = status.enabled ? status.state : 'disabled';
        setState(nextState);
        setCalibration(status.calibration ?? null);
        setError(nextState === 'error' ? (status.last_error ?? 'Camera error') : null);
        setPreviewFailed(false);
        if (nextState === 'running') {
          setFrameKey((key) => key + 1);
        }
      } catch {
        if (mounted && !controller.signal.aborted) {
          setState('offline');
          setCalibration(null);
          setError(null);
        }
      } finally {
        requestInFlight = false;
      }
    };
    void check();
    const timer = window.setInterval(() => void check(), 5000);
    return () => {
      mounted = false;
      controller.abort();
      window.clearInterval(timer);
    };
  }, []);

  const active = state === 'running' && !previewFailed;
  return (
    <div className="impact-workspace__empty" aria-label="USB camera preview">
      {active ? (
        <img
          alt="Live USB camera preview — not calibrated or measured"
          src={`${backendOrigin()}/api/camera/preview.jpg?frame=${frameKey}`}
          onLoad={() => setPreviewFailed(false)}
          onError={() => setPreviewFailed(true)}
          style={{ maxWidth: '100%', maxHeight: 180, objectFit: 'contain' }}
        />
      ) : (
        <span>{previewFailed ? 'Camera preview unavailable' : `Camera: ${state}`}</span>
      )}
      {error && <span role="alert">{error}</span>}
      <small>USB preview only · no impact measurement</small>
      <small aria-label="Camera calibration status">{calibrationLabel(calibration)}</small>
    </div>
  );
}
