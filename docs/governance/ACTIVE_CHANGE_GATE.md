# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 30

Title: Synthetic planar clubface pose from labelled image landmarks
State: Approved by Anders on 2026-11-09. Closeout requires same-SHA CI in draft PR #30.
Project Law: V1.
Branch: `gate30/synthetic-face-landmark-pose`.
Base: Gate 29 `9e924d5874f00f51792dddf620624f49a6587d62` (seven workflows successful).

## Scope and acceptance

Follow [Gate 30 synthetic face pose](GATE30_SYNTHETIC_FACE_POSE.md).
Reuse existing calibration, optical rays and pose representation. Allow an
offline pose helper, known synthetic point correspondences, focused tests
and governance documentation. Recover known translations and rotations,
reject ambiguous or inconsistent evidence, and verify final commit CI.

Stop for physical capture, new dependencies, automatic landmark detection,
or expansion into contact, runtime integration or physical claims.
