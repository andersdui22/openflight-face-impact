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

- Capture a genuine screenshot of the UI calibration status and attach it to PR #43 to satisfy the existing PR check. Do not use a fabricated screenshot or bypass the requirement.
- Verify UI format/build/lint/E2E, Python tests, USB fixtures, Pylint, foundation and documentation at the final SHA.
- Physical validation, stable physical camera-mode identity and impact accuracy remain outside the demonstrated evidence; do not close these by inference.
- PR #43 stays draft and unmerged until separately authorized.

## Acceptance interpretation

Gate 16 provides a reproducible **offline optics-profile pipeline** with pixel residual evidence and conservative status reporting. It does not yet demonstrate reproducible physical face-impact measurements or a verified ELP capture-mode binding. Those claims require actual hardware evidence and a separately approved validation step.
