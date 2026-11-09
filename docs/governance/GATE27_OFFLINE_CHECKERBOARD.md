# Gate 27 offline checkerboard calibration

Anders approved synthetic image calibration on 2026-11-09 and deferred all
physical testing. Gate 26 remains open at
`5ab6f698802fb5d990b0f6a076a0a834e49453c2`. The physical procedure and
its evidence requirements remain in draft PR #26.

## Source and reuse

The existing `SyntheticPlanarCalibration` is an affine pixel-to-plane map.
The existing `SyntheticCamera` projects known points with supplied ideal
intrinsics. Neither estimates camera intrinsics or lens distortion.
The experimental OpenFlight [checkerboard fitter](https://github.com/HarjotDhanota/openflight/blob/ea95a64329e5bbea52f901e3badb1cb07995a6fc/src/openflight/camera/checkerboard_calibration.py)
already lays out the board grid, fits intrinsics with OpenCV, and scores
separate views with those intrinsics frozen. Gate 27 adapts those parts
under AGPL-3.0-or-later and retains the source attribution in the module.
The experimental hardware mode profile and artifact contract are deferred
until a physical capture mode can be established.

## Evidence and limits

The offline function accepts in-memory grayscale images and an explicit
board layout and square size. It detects complete boards, rejects duplicate
images across both splits, and requires ten fit images and three validation
images of a common size. It rejects fit poses with less than ten degrees of
normal separation or a distance ratio below 1.15. These are software
screening thresholds adapted from the candidate, with no physical qualification.

Validation freezes the fitted intrinsics and distortion. A subset of the
corners estimates the pose of each separate validation view. The rest
measure pixel reprojection RMS against a budget supplied by the caller.
Synthetic tests also compare recovered intrinsics and corrected off-axis
rays with the known generator values. Pose diversity and pixel residuals
alone do not establish physical accuracy.

Acceptance requires positive synthetic image fitting, known-optics
checks, negative tests for missing or weak observations, and same-SHA
CI recorded in draft PR #27. No camera acquisition, calibration persistence,
UI integration, physical claims, merge, or release.
