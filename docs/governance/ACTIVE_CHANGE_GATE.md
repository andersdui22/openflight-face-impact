# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 16

Title: Synthetic finite rectangular clubface boundary validation
State: ACTIVE — user explicitly approved "Godkendt" following Gate 16 proposal (2026-11-09).
Project Law: V1 unchanged.
Working branch: `gate16/synthetic-finite-face-bounds`.
Base: Gate 15 `2bb7039112f4089170df916410a565e5900bedff`, six successful same-SHA workflows; draft PR #15 remains unmerged.

## Authorized scope
Define explicit positive finite synthetic face width and height in millimetres, centered on the Gate 14 face frame. Validate the Gate 15 synthetic contact point against finite rectangular face boundaries. Fail closed outside the face, with deterministic tests for center, edges, corners, just-outside positions and invalid dimensions. Reuse the existing synthetic sphere-plane contact logic rather than duplicating it.

## Acceptance
Clear inclusive boundary semantics and numerical tolerance; no inferred clubhead dimensions or physical precision. Same-SHA CI must pass.

## Exclusions
No curved face, grooves, actual clubhead mesh, real ball tracking, physical camera or accuracy validation, radar, UI, merge, release or Golden baseline.
