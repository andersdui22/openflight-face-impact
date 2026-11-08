# ACTIVE CHANGE GATE 05 — Synthetic camera calibration

State: ACTIVE — explicitly approved by user ("Godkendt") on 2026-11-08.
Project Law: V1, unchanged.
Repository: andersdui22/openflight-face-impact
Branch: gate05/synthetic-camera-calibration
Base: gate04/windows-elp-physical-validation @ 0a6aae04901d11b02b90fdc37d80005a731da866
Gate 04: eight of eight workflows successful on exact base SHA; draft PR #4 remains unmerged. Physical camera validation explicitly deferred by user.

## Objective
Reuse and evaluate OpenFlight's existing camera calibration/geometry code, develop narrowly scoped synthetic-image calibration with known dimensions, and verify coordinate transforms and unknown/uncertain measurement handling without physical hardware.

## Allowed
Read-only audit of existing geometry, calibration, tests, asset provenance and API/UI dependencies; narrowly scoped pure calibration code and synthetic fixtures; hardware-free tests and CI; evidence-backed documentation of units, coordinate conventions, handedness, transforms, limitations and uncertainty.

## Excluded
Physical ELP testing, hardware accuracy claims, Face Impact solver, clubface impact localization, unrelated UI redesign, ConnectorNext, MLM2PRO, BLE, radar, upstream edits, restricted 690CB assets, Golden nomination, merge, release and installer publication.

## Acceptance
1. Inventory existing reusable calibration and geometry functions with provenance and limitations.
2. Synthetic known-geometry calibration tests verify coordinate transforms and reject invalid/insufficient inputs.
3. No synthetic result is presented as physical camera calibration; no unmeasured lens, distance or sensor parameters are inferred.
4. Applicable CI green on final same SHA; PR remains draft and unmerged.

## Stop conditions
Missing evidence, remote drift, unsupported or restricted assets, physical validation needs, unapproved scope expansion, merge/release/Golden without separate approval.
