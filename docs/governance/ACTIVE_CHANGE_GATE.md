# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 13

Title: Single-camera synthetic pose observability and uncertainty
State: ACTIVE — user explicitly approved "Godkendt" after Gate 13 proposal (2026-11-08).
Project Law: V1 unchanged.
Working branch: `gate13/synthetic-pose-observability`.
Base: Gate 12 HEAD `32e09c5190316c082abe0d724acbeda8d9bc55e0`, six same-SHA successful workflows; draft PR #12 unmerged.

## Authorized scope
Analyze synthetic model poses at multiple explicitly supplied orientations/translations with one calibrated virtual camera. Quantify silhouette similarity, detect distinct poses with near-identical 2D projections, and fail closed when a unique pose cannot be resolved. Reuse Gate 11 projection and Gate 12 IoU fitting; deterministic synthetic tests and evidence only.

## Acceptance and evidence
Bounded candidate count, finite and validated rigid transforms, explicit ambiguity threshold, tests for clear and degenerate pose sets and invalid observations. Report observability as a candidate-set-specific synthetic metric, not physical angular accuracy. Same-SHA CI required.

## Exclusions
No physical camera, 850 nm IR measurement, real pose estimation, radar, impact mm, new UI, restricted clubhead mesh, merge, release or Golden baseline. Stop for new dependencies, incompatible upstream assumptions or unresolved CI.
