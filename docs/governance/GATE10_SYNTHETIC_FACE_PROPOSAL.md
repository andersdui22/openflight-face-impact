# Gate 10 — Automatic synthetic face-region proposal

State: ACTIVE. Explicit user approval: "Godkendt" (2026-11-08) to propose a face region automatically in synthetic IR images. Project Law V1 unchanged.
Base: Gate 09 `c7d881f300b02fc0c6f6f91039e8bbf5f493acf8`, latest PR #9 CI success for six workflows; draft and unmerged.

## Read-only evidence and rationale

At base SHA, `src/openflight/camera/synthetic_ir_face.py::locate_synthetic_ir_face` only recognizes a filled axis-aligned rectangle in a manually cropped fixture; `src/openflight/camera/synthetic_dual_pipeline.py` requires the caller to supply crop bounds. No reusable full-frame synthetic rectangle candidate proposal is present in those modules. A new narrowly scoped proposal helper can reuse the existing strict rectangle locator instead of replacing the detector.

## Allowed change and acceptance

Add a fixture-only function that automatically proposes a single full-frame bright rectangular candidate from a synthetic grayscale image containing a bright circular ball, using simple connected components and strict rectangular-mask verification. Reject zero or multiple candidates, partial shapes, out-of-frame regions, invalid image format or thresholds. Test deterministic positive and negative synthetic fixtures, preserve existing API behavior, update Handoff and validate same-SHA CI. No new dependencies.

## Exclusions and stop conditions

Not real clubface identification, physical image validation, pose estimation, face impact computation, metric units, production camera integration, merge, release or Golden baseline. Rectangle appearance alone does not prove clubface identity. Stop and investigate unexpected CI failures or source contract changes.
