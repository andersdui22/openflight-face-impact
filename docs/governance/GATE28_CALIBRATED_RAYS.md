# Gate 28 calibrated optical rays

Anders approved Gate 28 on 2026-11-09. The starting point is Gate 27
`3fde3dfa53dd8fb40683ebf694abcbb4a5aebc20`, verified on draft PR #27.
Gate 26 physical tests remain deferred.

## Reuse and scope

The existing affine map assumes a plane. The ideal mesh projection goes
from known 3D coordinates to pixels. Gate 28 instead inverts the
Brown-five model returned by the existing `CheckerboardCalibration`.

The experimental OpenFlight [calibrated projection](https://github.com/HarjotDhanota/openflight/blob/ea95a64329e5bbea52f901e3badb1cb07995a6fc/src/openflight/camera/calibrated_projection.py)
provides the basis for inversion, convergence and local fold checks.
The adaptation keeps AGPL-3.0-or-later attribution, reuses OpenCV for
inversion and forward projection, and stops at optical camera coordinates.
No rig transform, capture mode identity or depth is inferred.

## Contract and evidence

Input is a nonempty array of (column, row) pixels with an explicit image
size (width, height) equal to the calibration dimensions. Output is
ordered unit rays in a right/down/forward coordinate frame. The routine
rejects invalid optics, nonfinite or out-of-frame pixels, inverse projection
residual above 0.000001 pixel and locally folded distortion. The residual
threshold checks numerical consistency. Equal dimensions do not establish
that lens, crop or image orientation match across physical captures.

Synthetic tests check known off-axis rays, one ball centre and two clubface
points with the calibration fitted from Gate 27's generated boards, and
failure cases for invalid models and observations. No live capture, new
detector, pose, contact computation or physical accuracy claim.
Closeout requires exact-commit CI in draft PR #28.
