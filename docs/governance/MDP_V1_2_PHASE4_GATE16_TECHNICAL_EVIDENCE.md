# Gate 16 — technical evidence and remaining acceptance items

Status: **USER-APPROVED TECHNICAL CLOSEOUT / draft PR unmerged**. The user explicitly approved Gate 16 technical closeout with the documented offline-only limitations, and prohibited merge, release and physical ELP testing. This is not a physical ELP camera acceptance record.

## Implemented

- Reuse the existing offline checkerboard Brown-five fit and its separate held-out pixel-RMS validation.
- Version 1 JSON optics profile with strict schema and explicit camera-mode identity.
- Profile file persistence and fail-closed loading for missing or invalid files.
- Optional backend profile path via `OPENFLIGHT_FACE_IMPACT_CALIBRATION_PROFILE`.
- Calibration status in the existing USB status API and camera preview UI.
- Automated tests for roundtrip persistence, invalid profiles, mode mismatch at equal resolution, and no inferred physical compatibility.

## Evidence boundaries

- A stored profile can be read without opening the camera. The currently observed USB metadata does **not** establish a verified sensor mode, lens, crop, focus, or exposure configuration.
- The backend therefore supplies no trusted `camera_mode_id` to the compatibility check. Even a valid profile remains `mode_unknown`; `physical_validation` is always false.
- `fit_rms_px` and `validation_rms_px` are checkerboard image reprojection errors in **pixels**, not millimetre impact accuracy.
- `synthetic_offline` is the only permitted evidence kind in this Gate. Do not interpret it as real-camera validation.
- No physical ELP captures, camera measurements, user hardware tests, merges, or releases were performed.

## CI and open items

CI results must be evaluated against the **exact current PR head**; earlier green workflows are not proof that a later commit passed.

- **Deferred by user:** A genuine screenshot of the UI calibration status remains required by the existing PR check. The user has explicitly confirmed that this screenshot is postponed, as for Gates 14/15. The PR Checks workflow is expected to remain red for this documented reason; do not fabricate an image or use the `no-screenshots-needed` bypass for a visible UI change.
- **Verified baseline `64a4525e261b1e2fecfdb9b88f700e51cfabee36`:** all six technical workflows passed on this exact SHA: UI (format, build, lint, E2E), Tests, Face Impact Windows USB camera, Pylint, Face Impact foundation, Documentation. The seventh workflow, PR Checks, failed only on the deferred screenshot, with title and PR-content checks passing. This evidence is for that immutable SHA only; any subsequent documentation commit needs its own CI verification.
- Physical validation, stable physical camera-mode identity and impact accuracy remain outside the demonstrated evidence; do not close these by inference.
- PR #43 stays draft and unmerged until separately authorized.

## Acceptance interpretation

Gate 16 provides a reproducible **offline optics-profile pipeline** with pixel residual evidence and conservative status reporting. It does not yet demonstrate reproducible physical face-impact measurements or a verified ELP capture-mode binding. Those claims require actual hardware evidence and a separately approved validation step.

## User decision and closeout disposition (2026-11-11)

- **Decision:** User approved technical closeout of Gate 16 with the documented boundaries; no merge, release or physical ELP test.
- **Reviewed implementation SHA:** `83fab8d163bffcb7ce4001b0ef467eae0262f5ee`; draft PR #43, base `mdp-v1.2/phase3-gate14-15-integration` at `0915aef8ab3c132cf66d943764024ac75bbb0100`. The PR remains open and unmerged.
- **Same-SHA CI:** Documentation, Pylint, Face Impact foundation, Face Impact Windows USB camera, UI (build, lint, format, E2E) and Tests all completed successfully on the reviewed implementation SHA. PR Checks failed solely on the genuine screenshot requirement, expressly deferred by the user; no policy bypass was applied.
- **Accepted limitation:** Offline, synthetic checkerboard optics and pixel-RMS evidence only; no verified physical camera mode, lens/crop/focus/exposure identity, physical ELP captures or measured impact accuracy.
- **Disposition:** Technical implementation accepted for Gate 16; integration, screenshot and physical validation remain outstanding. This documentation-only commit is a new SHA and its own CI results must be checked separately before reporting it as green.
- **Next authority:** No Gate 17 implementation, merge or release authorized by this closeout. Read-only preparation for the next proposed Gate is permitted under Project Law V1.
