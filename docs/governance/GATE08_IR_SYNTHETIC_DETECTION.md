# Gate 08 — IR-style synthetic detection

Status: ACTIVE. Explicit user approval: "Godkendt", 2026-11-08, following proposal for IR-based image recognition with synthetic images only.

Base: Gate 07 `cb8d13451dac1648d2f5c4f8921a5663ad9eb621` (all six same-SHA workflows passed; draft PR #7 unmerged). Project Law V1 unchanged.

## Evidence and reuse

The existing `src/openflight/camera/detector.py::BallDetector` uses brightness thresholding, Gaussian blur and OpenCV HoughCircles, with a brightness/ring confidence heuristic. It assumes a bright IR-lit ball against a dark background; its actual ELP OV9281/850 nm performance is UNKNOWN. Reuse it unchanged first, with `CapturedFrame` fixtures, and document its observed successes/failures. Gate 07 synthetic red/green markers are NOT natural image recognition and must not be treated as such.

## Approved work

- Add deterministic hardware-free grayscale/IR-style synthetic image tests around the existing ball detector and its configurable parameters.
- Develop a narrow, separately named synthetic clubface-region candidate method for controlled high-contrast fixtures, if existing code has no suitable equivalent; reject ambiguity and do not claim pose or physical face identification.
- Test contrast, lighting and positions on synthetic frames; record limitations and future calibration integration needs.
- Preserve legacy API, camera acquisition, React/Electron UI and current behavior. Tests and minimal isolated pure processing code only.

## Stop conditions and exclusions

No real-camera acquisition or physical testing, no ELP/850 nm sensitivity claim, no natural-image accuracy claim, no impact computation, no club motion metrics, no automatic merge, release or Golden baseline. Stop and document any dependency/license/accuracy blocker. New code must not invent physical certainty from synthetic fixtures.
