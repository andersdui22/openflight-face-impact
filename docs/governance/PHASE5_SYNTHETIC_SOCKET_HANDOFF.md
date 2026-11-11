# Phase 5 — Synthetic Socket.IO handoff

This document records the software-only synthetic demonstration route.
It is not Gate acceptance or evidence of real ELP OV9281 measurements.

## Data path

1. The user explicitly clicks **Load synthetic motion demo** in the existing
   React/Electron Face Impact dashboard.
2. The UI emits `request_synthetic_motion_demo` with an acknowledgement callback.
3. The Flask-SocketIO handler constructs a deterministic synthetic sequence
   of grayscale ball/face images through `synthetic_motion_demo_response`.
4. The existing offline geometry and temporal analysis pipeline produces a
   JSON-compatible `synthetic_image_space_motion` payload.
5. The server emits `synthetic_motion_diagnostics` only to the requesting
   Socket.IO session. The UI validates its schema and fails closed on
   physical-contact claims, invalid distances and missing trend frames.
6. On socket disconnect the UI clears stale diagnostics.

## Explicit limitations

- No automatic real-camera capture analysis, hardware calibration, measured
  club-ball contact or millimetre impact precision is implied.
- This is an on-demand fixture, not a live video stream.
- The dashboard preview from design discussions is a target illustration,
  not a screenshot or evidence of implemented image replay.
- The integration test covers the real Flask-SocketIO event handler and
  requesting-session isolation; CI must pass for the exact commit SHA
  before any Gate closure is proposed.
- No upstream OpenFlight or ConnectorNext modifications, merges, releases
  or physical tests are authorized by this handoff.
