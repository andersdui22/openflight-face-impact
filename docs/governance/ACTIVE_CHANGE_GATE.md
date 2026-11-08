# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 14

Title: Synthetic clubface-local coordinate frame
State: ACTIVE — user explicitly approved "Godkendt" following Gate 14 proposal (2026-11-08).
Project Law: V1 unchanged.
Working branch: `gate14/synthetic-face-coordinate-frame`.
Base: Gate 13 `fbbbe9db38dcb4488372493fac1e985b7ae84e66`, six same-SHA successful workflows; draft PR #13 remains unmerged.

## Authorized scope
Define a synthetic clubface center and orthonormal local heel-to-toe and bottom-to-top axes with explicit units, handedness and right-handed surface normal. Transform synthetic 3D points into local face coordinates using an explicit rigid pose, and back. Reuse existing rigid transform conventions from Gates 11–13. Include deterministic tests for identity, rotation, translation, off-plane point, invalid frames and round-trip.

## Acceptance
No assumed real clubhead center or face dimensions. Reject nonfinite, degenerate, mirrored or inconsistent geometry and invalid pose. Coordinate units remain millimetres; surface normal direction is explicit. Same-SHA CI required.

## Exclusions
No actual ball/club contact measurement, real face recognition, physical camera test, calibrated precision, restricted club mesh, radar, UI, merge, release or Golden baseline. Stop for ambiguous real handedness or unverified asset assumptions.
