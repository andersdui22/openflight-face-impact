# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 28

Title: Optical rays from calibrated synthetic ball and face pixels
State: Approved by Anders on 2026-11-09. Closeout requires same-SHA CI in draft PR #28.
Project Law: V1.
Branch: `gate28/calibrated-optical-rays`.
Base: Gate 27 `3fde3dfa53dd8fb40683ebf694abcbb4a5aebc20` (seven workflows successful).

## Scope and acceptance

Follow [Gate 28 calibrated optical rays](GATE28_CALIBRATED_RAYS.md).
Reuse the offline checkerboard result and the existing OpenCV camera extra.
Allow an offline ray helper, synthetic tests and governance documentation.
Recover known optical directions in input order, reject invalid points
and mismatched dimensions, and verify GitHub CI on the final commit.

Stop for new dependencies, unlicensed source or assets, physical capture,
or expansion into detection, 3D pose, contact or runtime integration.
