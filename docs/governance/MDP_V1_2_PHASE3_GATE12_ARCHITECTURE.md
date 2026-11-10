# Phase 3 — Gate 12: single-owner camera architecture

Status: APPROVED FOR SCOPED DEVELOPMENT; NOT ACCEPTED.
Approval: user explicitly approved Gate 12 and autonomous continuation under Project Law V1 on 2026-11-10.
Base SHA: `79549289b7de332a3752f90911850346bcd9fcf0`.
Branch: `mdp-v1.2/phase3-gate12-camera-architecture`. Base is Phase 2 draft PR #37 branch; no merge or release authorization.

## Problem and objective
Connect the existing Windows ELP OV9281 USB acquisition architecture to the existing six-panel Face Impact UI in later gates without duplicate camera ownership, misleading timing/FPS or a second UI/backend stack. Gate 12 is architectural inventory, explicit interface design and hardware-free tests; **not** real UI camera integration, physical capture, calibration or impact measurement.

## Read-only evidence inventory
- `src/openflight/camera/windows_usb.py`: `WindowsUsbCamera` owns one OpenCV DirectShow capture and reader thread; `UsbCameraSettings` includes device index, requested width/height/FPS and ring sizing. Its `TriggeredFrameBuffer` receives grayscale frames. `negotiated.reported_fps` is a device-reported value; `delivered_fps` is calculated from host arrival times. Exposure/gain remain unknown; the host timestamp is not sensor exposure time.
- `src/openflight/camera/triggered_buffer.py`: existing ring and capture semantics to reuse.
- `src/openflight/camera/capture_runtime.py`: Pi-specific `CameraCaptureRuntime` and camera ring; do not start it concurrently as another owner for the Windows USB device.
- `ui/src/components/CameraFeed.tsx`: legacy OpenFlight UI consumes `/api/camera/preview.jpg`, `/api/camera/usb/status` and exposure-quality endpoints; it is **not** yet the Face Impact dashboard preview integration.
- `ui/electron/main.js` and `scripts/build-face-impact-windows.ps1`: portable Electron UI can launch on Windows, but does not bundle or start the Python camera backend.
- `tests/test_windows_usb_camera.py` and UI camera tests: existing hardware-free tests to inspect/reuse rather than duplicate.
- `docs/governance/GATE03_WINDOWS_ELP_CAMERA.md`: prior camera acquisition scope and source evidence; historical gate authorization does not grant Gate 13 implementation.

## Proposed contract for subsequent integration (design only)
1. Exactly one backend `WindowsUsbCamera` instance owns the selected Windows camera, reader thread and frame ring for the active session. UI and downstream shot processing subscribe to the same owner; neither opens the device.
2. A service boundary exposes device selection, lifecycle (`disabled | starting | running | stopped | error`), negotiated width/height/device-reported FPS, observed host-arrival FPS, frame counts and last error. Never represent requested or reported FPS as independently measured sensor FPS.
3. Preview consumes a bounded, read-only projection of frames from the owner. A slow preview client cannot block acquisition; a shot/capture consumer cannot create its own reader or mutate the preview stream.
4. Start/stop and disconnect/reconnect must be idempotent or fail with explicit state; no silent second owner. Session and frame identity must prevent stale results after reconnect.
5. Any frame metadata must distinguish host arrival time from genuine sensor exposure timestamps. Unknown exposure, gain, calibration, impact position and measurement precision remain unknown.
6. Electron/Python process lifecycle, packaging and security policy require separate implementation evidence; the Phase 2 EXE is currently UI-only.

## Gate 12 acceptance and stop conditions
- Inspect existing service/routes, USB tests and UI tests; record actual compatibility gaps and non-duplication rationale.
- Implement only narrow interface/contract tests where evidence warrants; no new production capture loop or broad refactor.
- Verify targeted tests and required exact-HEAD CI, with any screenshot-in-PR-description requirement still deferred but **not waived**.
- Do not proceed to Gate 13, physical tests, merge or release without separate approval.
- If an actual API/ownership mismatch requires a public behavior change, document and stop for scope review.
