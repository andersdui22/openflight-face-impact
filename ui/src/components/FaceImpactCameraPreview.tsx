import { useEffect, useState } from 'react';
import { getServerOrigin } from '../utils/serverOrigin';

type CameraState = 'checking' | 'disabled' | 'starting' | 'running' | 'stopped' | 'error' | 'offline';

interface UsbStatus {
  enabled: boolean;
  state: 'disabled' | 'starting' | 'running' | 'stopped' | 'error';
  last_error?: string | null;
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

  useEffect(() => {
    const controller = new AbortController();
    let mounted = true;
    const check = async () => {
      try {
        const response = await fetch(`${backendOrigin()}/api/camera/usb/status`, {
          signal: controller.signal,
          cache: 'no-store',
        });
        if (!response.ok) throw new Error('Camera service unavailable');
        const status = (await response.json()) as UsbStatus;
        if (!mounted) return;
        const nextState: CameraState =
          status.enabled && ['disabled', 'starting', 'running', 'stopped', 'error'].includes(status.state)
            ? status.state
            : 'disabled';
        setState(nextState);
        setError(nextState === 'error' ? status.last_error ?? 'Camera error' : null);
        if (nextState === 'running') {
          setPreviewFailed(false);
          setFrameKey((key) => key + 1);
        } else {
          setPreviewFailed(false);
        }
      } catch {
        if (mounted && !controller.signal.aborted) {
          setState('offline');
          setError(null);
        }
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
    </div>
  );
}
