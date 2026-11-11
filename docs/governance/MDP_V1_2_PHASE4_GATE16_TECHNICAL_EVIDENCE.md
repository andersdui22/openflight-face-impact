# Gate 16 — technical evidence and remaining acceptance items

Status: **OPEN / not merged**. This report documents only automated, hardware-free evidence; it is not a physical ELP camera acceptance record.

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
