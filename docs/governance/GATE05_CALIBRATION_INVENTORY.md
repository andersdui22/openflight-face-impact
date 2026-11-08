# Gate 05 — read-only calibration inventory (initial)

Repository: `andersdui22/openflight-face-impact`
Baseline: Gate 04 `0a6aae04901d11b02b90fdc37d80005a731da866`
Evidence class: source inspection only, not physical camera evidence.

## Reusable functions

- `src/openflight/camera/geometry.py::deroll_normalized_offsets`: pure clockwise preview-roll correction, taking horizontal and **up-positive** vertical normalized offsets. Supports scalars and NumPy arrays. Existing tests in `tests/test_camera_geometry.py` verify zero roll and synthetic sloped-line correction. It does **not** calibrate intrinsic camera parameters, perspective, physical scale or lens distortion.
- `src/openflight/camera/detector.py::BallDetector`: image-space ball localization, not a physical camera calibration routine. Its documented setup is an IR-lit ball against a dark background, viewed from behind the tee. No evidence yet that its assumptions hold for a side-mounted ELP OV9281.
- `src/openflight/camera/club_delivery.py`: experimental camera/radar-fusion club-delivery logic. Depends on IWR6843 and OPS measurements, which are out of scope for this single-camera Face Impact project. Its use of `deroll_normalized_offsets` supports reuse of the **pure geometry helper only**, not the radar-dependent estimator.

## Conventions and limitations

- Pixel coordinates are typically image-column right and image-row down; normalized vertical offsets passed to `deroll_normalized_offsets` are explicitly up-positive.
- No intrinsic matrix, lens distortion coefficients, working distance, field of view, metric pixel scale, face plane, or handedness transform is verified for the user's physical ELP OV9281.
- Synthetic targets with known dimensions can validate mathematical consistency, but cannot establish a real-world millimeter accuracy or clubface impact position.
- No third-party model or restricted 690CB mesh is required for the proposed pure coordinate tests.

## Next bounded work

Build a pure synthetic planar coordinate-transform helper with explicit known reference points and millimeter units, reject degenerate geometry, and verify forward/inverse transforms on generated points. Do not wire it into live acquisition or claim physical calibration until hardware evidence exists.
