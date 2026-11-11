# Phase 4 Gates 17–19 — parallel startup audit and implementation boundary

Status: **USER-APPROVED PARALLEL DEVELOPMENT; IMPLEMENTATION AND CI IN PROGRESS** (2026-11-11). This document is a scope record, not acceptance evidence or a claim of completed gates.

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
- **Plan wording recovered from the prior user-approved Master Development Plan V1.2 conversation (2026-11-09):** Gate 17 “Køllefladens position, orientering og referencepunkter”, acceptance “Koordinatsystemer og transformeringer verificeret”; Gate 18 “Køllespecifikke fysiske modeller og dimensioner”, acceptance driver, wood, iron and wedge each handled according to its actual geometry; Gate 19 “Kalibreringsworkflow, lagring og kontrol af gyldighed”, acceptance rejection of invalid or outdated calibration. This is conversation-derived plan evidence, **not** a verified copy of the plan file in GitHub. The exact canonical plan document path remains unlocated.

## Parallel workstreams and provisional boundaries

### Gate 17 — Køllefladens position, orientering og referencepunkter

Scope: establish explicit camera, image and clubface coordinate conventions, unit and handedness semantics; pure validated transformations, only where existing implementation lacks them. No assumed 3D depth or physical pose from a single image.

Acceptance proposal: deterministic synthetic round-trip/reference tests; reject degenerate, nonfinite and ambiguous transforms; provenance of every coordinate convention; no inferred physical accuracy.

### Gate 18 — Køllespecifikke fysiske modeller og dimensioner

Scope: typed club-model metadata and geometric reference definitions for driver, woods, irons and wedges, with unknown dimensions represented as unknown rather than fabricated nominal measurements. Reuse existing admitted model/geometry modules and asset licenses.

Acceptance proposal: explicit model provenance, coordinate-frame compatibility with Gate 17, nonfinite/invalid dimension rejection and deterministic synthetic fixtures; no restricted mesh reuse.

### Gate 19 — Kalibreringsworkflow, lagring og kontrol af gyldighed

Scope: reuse Gate 16's versioned optics profiles and persistence; add only needed pure validation and lifecycle checks for calibration/profile/model associations, stale or incompatible profiles and transparent UI status.

Acceptance proposal: fail-closed mismatch/staleness tests, no extra camera reader, honest offline vs physically verified status, no automatic impact accuracy claims.

## Dependencies and sequencing

1. Audit existing geometry, model and calibration code; reconcile the recovered user-approved Gate definitions and record any difference from the canonical plan file if located.
2. Gate 17's coordinate contract must be settled before Gate 18 consumes it; Gate 19 can independently audit profile lifecycle in parallel.
3. Implement in separate, small reviewable changes; run focused regression tests and same-SHA CI for the shared integration head.
4. Record individual Gate 17, 18 and 19 evidence and separate technical closeout decisions. Parallel authorization does not imply automatic closeout.

## Stop conditions

- Stop production-code changes if authoritative Gate definitions differ materially, the required source/asset license or provenance is missing, or a task exceeds the user-approved boundary.
- No physical camera capture, claimed millimetre impact precision, second USB acquisition owner, ConnectorNext/MLM2PRO/radar/GSPro work, destructive Git operations, merge, release or EXE validation.
- No fabricated screenshot or bypass of the previously deferred screenshot PR requirement.
- Unknown camera/lens/crop/mode, club geometry, pose and depth must remain UNKNOWN pending evidence.


## Implementation evidence and remaining acceptance (2026-11-11)

This is a progress inventory, **not** a gate closeout. The three workstreams share draft PR #44, based on Gate 16 closeout. A prior integrated commit `355fe47045f4b6a354c8623abf79bc741d4b03a0` passed all six CI workflows. Later commits require independent same-SHA verification before acceptance.

| Gate | Implemented offline evidence | Not yet established |
| --- | --- | --- |
| 17 | `rigid_frame.py`, `face_reference_points.py`, `planar_face_reference.py`; synthetic inverse/compose, proper rotation and reference-point tests | Real camera-to-face pose, actual club orientation, pixel-to-face intersection/depth, physical impact point |
| 18 | `club_face_model.py`; driver/wood/iron/wedge families, optional provenance-tagged dimensions, planar versus curved metadata, synthetic tests | Real measured club geometries, actual curved-surface solver, sourced model assets/licensing, physical geometry verification |
| 19 | `calibration_revision.py`, `calibration_revision_status.py`, `calibration_club_binding.py`; offline revision/mode/model identity guards and tests | Persisted independent revision binding integrated into active workflow, reliable camera mode identity, physically measured calibration, user-facing lifecycle UI |

### Coordinate and provenance contract

- The camera optical rays already use +X right, +Y down, +Z forward; **do not** assume that convention is interchangeable with the face-local coordinate frame.
- Synthetic face-local model: +X toward toe, +Y toward crown/topline, +Z outward from the striking face, in millimeters. This is an explicitly *declared* model convention, not a detected orientation or handedness correction.
- `RigidFrameTransform` only applies a caller-supplied proper rotation and XYZ-mm translation. A camera-from-face transform must be established independently; this implementation does not estimate one.
- The planar model treats a dimensioned face as a centered rectangular reference **for synthetic tests only**. Actual striking-face boundaries may not be rectangular, and curved faces are rejected rather than flattened.
- The Gate 18 `evidence_source` string is provenance metadata, **not verification** that a measurement or source is trustworthy. Synthetic fixtures must never be represented as real club specifications.
- A SHA-256 revision is a byte-level offline profile identity, **not** calibration expiry, physical mode verification or calibration accuracy. A caller must persist the expected revision independently; deriving it from the candidate profile at check time defeats stale detection.
- `CalibrationClubBinding` binds a revision to a model identifier, **not** the geometry contents. Changing dimensions under the same model identifier is not detected by that binding; model geometry versioning or a content digest is required before production use.

### Review and stop decision

No individual Gate 17, 18 or 19 is accepted yet. Continue with focused tests, same-SHA CI, provenance-aware geometry revision validation and integration design. Do not merge, release, perform physical ELP testing or claim millimeter impact precision.
