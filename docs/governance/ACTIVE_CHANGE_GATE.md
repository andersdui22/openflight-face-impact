# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 27

Title: Offline checkerboard calibration with synthetic images
State: Approved by Anders on 2026-11-09. Closeout requires same-SHA CI evidence in draft PR #27.
Project Law: V1.
Branch: `gate27/offline-checkerboard-calibration`.
Base: Gate 26 `5ab6f698802fb5d990b0f6a076a0a834e49453c2`, automated checks successful. Physical evidence deferred by Anders.

## Scope and acceptance

Follow [Gate 27 offline checkerboard calibration](GATE27_OFFLINE_CHECKERBOARD.md).
Reuse the existing OpenCV camera extra and the experimental OpenFlight
fit/validation approach. Scope covers a pure offline calibration module,
synthetic image fixtures and focused tests, and governance documentation.
Confirm recovered optics against known synthetic optics, validate on
separate images, reject insufficient evidence, and verify GitHub CI.

Stop for physical capture or evidence, unlicensed code/assets, new
dependencies or expansion into runtime, capture or UI integration.
