# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 12

Title: Synthetic silhouette-based clubhead pose candidate estimation
State: ACTIVE — user explicitly approved "Godkendt" following Gate 12 proposal, 2026-11-08.
Project Law: V1 unchanged.
Working branch: `gate12/synthetic-mesh-pose`.
Base: Gate 11 `a45bbc93274cac42affe0545b3a06461eb1061a3`; six successful CI workflows on that SHA; draft PR #11 remains unmerged.

## Authorized scope
Compare a known synthetic observed silhouette against rendered projections of a supplied synthetic triangle mesh, using explicit camera intrinsics/extrinsics and finite candidate poses. Reuse the Gate 11 projection and upstream OpenFlight experimental IoU concept (open-flight/openflight PR #250 `fit.py`), without its radar geometry. Provide deterministic synthetic tests for recovered pose, invalid observations and ambiguity.

## Acceptance
No imported restricted 690CB mesh or model; explicit finite candidate set and bounded computation; fail closed on no match, invalid candidates and ambiguous equivalent projections. Keep result labeled synthetic and unvalidated. CI must pass on exact final HEAD.

## Exclusions and stop conditions
No real-image detection, physical ELP tests, radar, millimetre Face Impact calculation, actual 6DOF precision claim, UI redesign, merge, release or Golden baseline. Stop if source license, tests or calibration assumptions cannot be verified.
