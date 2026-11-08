# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 15

Title: Synthetic sphere-to-planar-clubface contact geometry
State: ACTIVE — user explicitly approved "Godkendt" after Gate 15 proposal (2026-11-08).
Project Law: V1 unchanged.
Working branch: `gate15/synthetic-ball-face-contact`.
Base: Gate 14 `eb0ab8e28749758db06274a4214eaec1748bb3df`, six successful same-SHA workflows; draft PR #14 unmerged.

## Authorized scope
Calculate the synthetic contact point of a sphere with an infinite planar face of explicit outward normal and center. Use Gate 14 local heel/toe and vertical axes to return signed millimetre offsets and a simple direction classification. Require explicit positive ball radius, sphere center and an actual tangent configuration within a numerical tolerance. Reject gaps, interpenetration, wrong-side geometry, invalid frames, unknown radius and ambiguous states. Deterministic synthetic tests for center, heel/toe, high/low, transformed pose, gaps and invalid geometry.

## Acceptance
No inferred ball radius, actual face dimensions, clubhead shape or physical impact. Report only a unique synthetic tangent point; no extrapolation from nearby but non-contacting states. Keep mm and model convention explicit. Same-SHA CI required.

## Exclusions
No real ball detection, motion inference, camera validation, real clubface surface curvature, impact dynamics, physical test, radar, UI, merge, release or Golden baseline.
