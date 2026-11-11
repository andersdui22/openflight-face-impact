# Gate 16 — camera calibration profile and integration

Status: **USER APPROVED — implementation in progress** (2026-11-11).

## Baseline and authority
- Master Development Plan V1.2, Phase 4 Gate 16: camera calibration, lens distortion, calibration profile; reproducible results with documented error.
- Project Law V1 applies.
- Gate 16 branch: `mdp-v1.2/phase4-gate16-camera-calibration`.
- Immutable starting SHA: `0915aef8ab3c132cf66d943764024ac75bbb0100`, the technically closed Gate 14/15 integration. Seven workflows passed on this SHA.
- PR #42 and Gate 14/15 PRs remain draft/unmerged; screenshot deferrals are not waived.

## Approved implementation scope
1. Reuse `checkerboard_calibration.calibrate_checkerboard`; do not duplicate fitting mathematics.
2. Define a versioned, explicit calibration profile for Brown-five intrinsics, distortion, image dimensions, residual evidence, and known camera-mode identity.
3. Validate serialized profiles strictly, including finite values, canonical matrix, image size, coefficient count, version and camera-mode compatibility. Never infer physical validity from equal resolution alone.
4. Expose calibration status safely to the existing UI without creating a second USB camera reader or changing the shared frame ring.
5. Distinguish synthetic/offline evidence from physically verified calibration; never label unverified profiles as physical measurement.
6. Add hardware-free regression tests for round trips, invalid profiles, incompatible mode, and deterministic optics, and run same-SHA CI.

## Explicit exclusions
No physical ELP OV9281 capture or accuracy claim; no automatic clubface/impact measurement, additional capture loop, ConnectorNext, MLM2PRO, radar, GSPro, merge, release, or Windows EXE packaging validation.

## Audit evidence
- Existing `src/openflight/camera/checkerboard_calibration.py` fits Brown-five intrinsics using 10 fit and 3 held-out validation checkerboard images and records reprojection RMS.
- Existing `src/openflight/camera/calibrated_rays.py` validates intrinsics and rejects mismatched image sizes; optical rays have no inferred depth.
- Existing `src/openflight/camera/synthetic_calibration.py` is an affine planar test utility, not a physical optics model.
- Existing `ui/src/components/FaceImpactCameraPreview.tsx` shows camera state and explicitly labels preview as not calibrated or measured.
- No physical hardware mode identity or validation evidence is established.

## Acceptance evidence still required
Implementation review, targeted regression tests, all required CI workflows on exact implementation SHA, draft PR evidence, and explicit user technical closeout approval. This document records scope, **not** a claim that Gate 16 has passed.
