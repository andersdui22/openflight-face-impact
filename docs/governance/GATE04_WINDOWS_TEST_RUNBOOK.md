# Gate 04 — Windows ELP OV9281 operator test preparation

This is a development test, not a released installer, calibrated measurement, or physical Golden baseline. The user approved Gate 04 preparation and physical validation, but the exact procedure and participation must be agreed before any physical test.

## Developer prerequisites

Windows PC, Python 3.12, Node.js matching `.node-version`, npm, this fork checked out on `gate04/windows-elp-physical-validation`, and an ELP OV9281 USB camera. Close OBS, AMCap, Windows Camera and any other application holding the camera.

From the repository root in PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[camera]"
cd ui
npm ci
npm run build
cd ..
$env:OPENFLIGHT_PYTHON = (Resolve-Path .\.venv\Scripts\python.exe).Path
$env:OPENFLIGHT_USB_CAMERA_INDEX = "0"
node scripts/windows-bootstrap.mjs
```

The opt-in environment variable selects an OpenCV DirectShow device **index**, not a stable ELP device identity. If index 0 selects another device or fails, stop the program before changing the index to 1, 2, etc. The launcher still runs the backend in mock mode for unrelated inherited OpenFlight features. It uses the existing single USB acquisition reader and Electron UI.

## Planned physical evidence (not yet collected)

- Windows version, camera model/USB identifier, OpenCV version and tested device index.
- Requested and negotiated width, height and **driver-reported** FPS from `http://127.0.0.1:8080/api/camera/usb/status`.
- Preview result, whether frames_received increases over a timed interval, frame interruptions, stop/restart behavior, error messages and relevant log output.
- **Delivered FPS** requires a timed frame-count measurement with defined start/end timestamps; do not label the driver-reported FPS as delivered FPS.
- Note whether the camera is in use by another application. Do not perform golf swings or impact measurement in this gate.

## Limits

No Windows installer exists yet. The camera has not been physically validated, stable device enumeration is not implemented, and the Electron UI retains Pi-specific controls that are not USB functions. This runbook does not claim that camera indexing, FPS, or exposure settings work on the user's physical computer.
