# ACTIVE CHANGE GATE 03 — Windows ELP OV9281 USB camera acquisition

State: ACTIVE — explicitly approved by the user on 2026-11-08.
Project Law: V1, unchanged.
Repository: andersdui22/openflight-face-impact
Branch: gate03/windows-elp-camera
Base: gate02/windows-bootstrap @ 546eff3f9a761891e16178de40afc617b29960ed
Gate 02: eight of eight CI workflows succeeded on the exact base SHA; draft PR #2 remains unmerged.
Authorization: "Jeg godkender Gate 03 for ELP OV9281 USB-kameraintegration på Windows med den beskrevne afgrænsning. Fortsæt udviklingen autonomt inden for Project Law V1."

## Objective
Integrate a single ELP OV9281 USB camera on Windows using the existing OpenFlight camera architecture. Identify/select the Windows camera, open and acquire frames, report actual supported width/height/FPS, feed existing buffered-frame functionality without duplicate acquisition ownership, and handle start/stop/errors/reconnection. Use hardware-free mocks for CI; never claim physical FPS or impact precision.

## Allowed changes
Narrow Windows camera adapter and integration points in existing Python camera modules; narrowly required dependency/configuration changes with Windows evidence; focused unit tests and Windows CI; documentation and draft stacked PR. Reuse existing `TriggeredFrameBuffer` and capture lifecycle. Review existing implementations before adding new ones. Any timestamp supplied by the host is labeled host-arrival time, not sensor exposure.

## Excluded
Face Impact solver, clubhead geometry, pose, calibration claims, shot/first-contact inference, radar, MLM2PRO, BLE, ConnectorNext, unrelated UI redesign, physical hardware test, Golden, installer, merge or release.

## Acceptance
1. A single acquisition owner can select/open a Windows USB camera, expose honest negotiated resolution/FPS and deliver frames to the existing buffer.
2. Start, stop, device errors and reconnection are bounded and tested without hardware.
3. Existing Pi capture and unrelated OpenFlight behavior remain unchanged.
4. CI passes on the exact final SHA; no physical camera validation is claimed.
5. Draft PR is unmerged; evidence and remaining physical validation gaps documented.

## Stop conditions
Unapproved expansion, incompatible or unlicensed dependency, absent required evidence, physical test, destructive Git operation or merge/release without explicit authorization.

## Read-only source evidence
`src/openflight/camera/capture_runtime.py` currently owns Pi `Picamera2` capture and uses `TriggeredFrameBuffer` from `src/openflight/camera/triggered_buffer.py`. Windows USB device capture is not implemented there. Preserve the Pi implementation and avoid a second simultaneous acquisition owner. The Phase 0 audit and candidate register identify unvalidated experimental Face Impact work, which is not admitted under this gate.
