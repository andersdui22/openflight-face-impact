# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 17

Title: Synthetic polygonal clubface footprint
State: ACTIVE — user explicitly approved "Godkendt" (2026-11-09).
Project Law: V1 unchanged.
Working branch: `gate17/synthetic-face-polygon`.
Base: Gate 16 `8915eb7f418b1eebf08e2c92a56e87edabee5ba7`, six successful same-SHA workflows; draft PR #16 unmerged.

## Authorized scope
Represent a synthetic planar clubface boundary by explicit 2D local (heel/toe, vertical) vertices in millimetres. Support convex and concave simple polygons, including asymmetric shapes, with inclusive edges and corners. Reject malformed, degenerate, self-intersecting or nonfinite polygon geometry. Reuse Gate 15 sphere-plane tangent point and Gate 14 coordinate conventions. Deterministic tests for center, edges, corners, asymmetric concave cutout, exterior points and invalid geometry.

## Acceptance
Boundary containment is exact up to documented floating-point numerical considerations, without widening the synthetic shape. Same-SHA CI required.

## Exclusions
No real clubface geometry, camera calibration or physical validation, curvature, radar, UI, merge, release or Golden baseline.
