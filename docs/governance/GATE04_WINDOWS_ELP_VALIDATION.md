# ACTIVE CHANGE GATE 04 — Windows ELP OV9281 physical camera validation

State: ACTIVE — explicitly approved by the user on 2026-11-08 ("Godkendt" in response to the Gate 04 proposal).
Project Law: V1, unchanged.
Repository: andersdui22/openflight-face-impact
Branch: gate04/windows-elp-physical-validation
Base: gate03/windows-elp-camera @ 387c088cf338ccd1c55a4e1f065980a047d75dbc
Gate 03: seven required workflows passed on this exact SHA; PR #3 remains draft and unmerged.

## Objective
Prepare a reproducible, easy-to-run Windows test path for a single physical ELP OV9281 USB camera and validate real device selection, live preview, delivered FPS, stability and failure logging using user-operated hardware.

## Allowed
Read-only review of existing Windows launcher, USB adapter, runbook, CI and React UI; narrowly scoped Windows test setup/scripts and diagnostics; camera enumeration/selection and actual delivered-FPS measurement when clearly distinguished from driver-reported FPS; focused regression tests; test logs and evidence templates; user-guided physical camera validation **only after agreeing the exact procedure and participation**. Prefer existing architecture and one acquisition owner.

## Excluded
Face Impact calculation, pose/geometry, calibration, ball/face localization, unrelated UI redesign, ConnectorNext, MLM2PRO, BLE, upstream repository edits, Golden nomination, merge, release or published installer. No automatic access to the user's Windows computer or camera.

## Acceptance
1. A documented reproducible Windows setup and test procedure with clear prerequisites, camera index selection, start/stop and troubleshooting.
2. Explicit distinction between actual delivered FPS and camera-driver-reported FPS, plus reliable evidence/log capture.
3. Hardware-free tests and applicable CI green on final same SHA; physical validation results recorded only if performed by user.
4. Honest list of untested hardware conditions and outstanding issues; draft PR remains unmerged.

## Stop conditions
Missing physical participation or evidence; unexpected remote drift; destructive operations; unsupported dependencies; unapproved scope expansion; merge/release/Golden without explicit approval.
