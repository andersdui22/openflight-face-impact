# Phase 4 Gates 17–19 — parallel startup audit and implementation boundary

Status: **USER-APPROVED PARALLEL DEVELOPMENT; READ-ONLY AUDIT IN PROGRESS** (2026-11-11). This document is a scope record, not acceptance evidence or a claim of completed gates.

## Authorization and baseline

- User explicitly approved parallel development of Gates 17, 18 and 19, requiring a read-only audit, documented scope, dependencies, acceptance criteria and stop conditions before implementation; hardware-free tests and CI are allowed.
- Project Law V1 applies. No merge, release or physical ELP test is authorized.
- Working branch: `mdp-v1.2/phase4-gates17-19-parallel`, created from Gate 16 technical-closeout commit `21ad7a70833652603c7d4326fb28a6b099669629`.
- Gate 16 PR #43 is draft/unmerged; its reviewed implementation SHA `83fab8d163bffcb7ce4001b0ef467eae0262f5ee` passed six technical workflows; the screenshot PR check was explicitly deferred. The Gate 16 closeout documentation commit was still undergoing CI at startup.
- This branch is an integration workspace for the three approved gates, **not** a merge into default or an authorization to rewrite prior work.

## Read-only source audit (known evidence)

- `docs/governance/PROJECT_LAW.md`: Project Law V1 requires read-only audit, reuse, explicit coordinate/unit conventions, one camera acquisition owner, same-SHA CI and independent gate closeout.
- `src/openflight/camera/calibrated_rays.py`: existing Brown-five pixel-to-optical-unit-ray conversion; image pixel coordinates (column,row), camera rays +x right, +y down, +z forward; **no depth inferred**. Reuse rather than duplicate.
- `src/openflight/camera/synthetic_calibration.py`: synthetic affine planar pixel-to-mm utility, explicitly **not** a physically calibrated camera model.
- Gate 16 calibration profiles: strict versioned offline optics, mode identity, fail-closed profile loading; runtime does not establish a trusted physical mode, so status remains `mode_unknown` and `physical_validation=false`.
- **Unresolved authoritative-plan audit:** exact Gate 17–19 wording and acceptance criteria in Master Development Plan V1.2 have not yet been independently located in repository file paths. The user-facing proposed areas below are provisional until reconciled with the authoritative plan. Do not silently substitute provisional wording for that plan.

## Parallel workstreams and provisional boundaries

### Gate 17 — coordinate frames and clubhead pose references

Scope: establish explicit camera, image and clubface coordinate conventions, unit and handedness semantics; pure validated transformations, only where existing implementation lacks them. No assumed 3D depth or physical pose from a single image.

Acceptance proposal: deterministic synthetic round-trip/reference tests; reject degenerate, nonfinite and ambiguous transforms; provenance of every coordinate convention; no inferred physical accuracy.

### Gate 18 — club-specific geometry/model identity

Scope: typed club-model metadata and geometric reference definitions for driver, woods, irons and wedges, with unknown dimensions represented as unknown rather than fabricated nominal measurements. Reuse existing admitted model/geometry modules and asset licenses.

Acceptance proposal: explicit model provenance, coordinate-frame compatibility with Gate 17, nonfinite/invalid dimension rejection and deterministic synthetic fixtures; no restricted mesh reuse.

### Gate 19 — calibration workflow, persistence and validity

Scope: reuse Gate 16's versioned optics profiles and persistence; add only needed pure validation and lifecycle checks for calibration/profile/model associations, stale or incompatible profiles and transparent UI status.

Acceptance proposal: fail-closed mismatch/staleness tests, no extra camera reader, honest offline vs physically verified status, no automatic impact accuracy claims.

## Dependencies and sequencing

1. Audit existing geometry, model and calibration code and reconcile exact Master Development Plan gate definitions before production-code edits.
2. Gate 17's coordinate contract must be settled before Gate 18 consumes it; Gate 19 can independently audit profile lifecycle in parallel.
3. Implement in separate, small reviewable changes; run focused regression tests and same-SHA CI for the shared integration head.
4. Record individual Gate 17, 18 and 19 evidence and separate technical closeout decisions. Parallel authorization does not imply automatic closeout.

## Stop conditions

- Stop production-code changes if authoritative Gate definitions differ materially, the required source/asset license or provenance is missing, or a task exceeds the user-approved boundary.
- No physical camera capture, claimed millimetre impact precision, second USB acquisition owner, ConnectorNext/MLM2PRO/radar/GSPro work, destructive Git operations, merge, release or EXE validation.
- No fabricated screenshot or bypass of the previously deferred screenshot PR requirement.
- Unknown camera/lens/crop/mode, club geometry, pose and depth must remain UNKNOWN pending evidence.
