# Gate 30 synthetic clubface pose

Anders approved a synthetic planar face pose estimate on 2026-11-09.
Gate 29 `9e924d5874f00f51792dddf620624f49a6587d62` is the base.
Physical tests remain deferred under Gate 26.

## Reuse and method

Gate 28 converts observed pixels to corrected optical directions. The
existing silhouette matcher ranks supplied poses by mask overlap, while the
checkerboard fitter estimates validation board pose with OpenCV. Gate 30
reuses the calibrated directions and the existing rigid pose representation.
The landmark solver uses OpenCV's planar IPPE to obtain candidate poses from
known point correspondences. This is separate from silhouette matching and
the experimental outline/shaft fit, whose inputs are different.
[OpenCV planar pose documentation](https://docs.opencv.org/5.0/main_modules/d_projection.html)

## Contract and evidence

Supply at least four distinct, spread-out face-local landmark positions in
millimetres and the corresponding pixels in matching order. The landmarks
lie on the model's z=0 plane. Model x points from heel to toe, y points
from bottom to top, and +z is the outward normal of the visible face.
The output uses right/down/forward optical camera coordinates. For the
existing `SyntheticPoseCandidate` contract, the camera frame is the world.

Candidate scoring uses RMS reprojection in the original distorted image.
Reject solutions behind the camera or showing the back of the model face.
Accept only if the best result satisfies the caller's pixel RMS limit and
beats the next valid candidate by the caller's minimum pixel margin.
The margin checks ambiguity for the supplied data. It is not a physical
error bound.

Tests recover known metric positions and orientations through distortion,
verify an existing face-frame transform, and reject ambiguity, bad point
pairings, a back-facing plane, poor spread and mismatched image dimensions.
The known point pairings are synthetic inputs. Physical point detection,
contact integration, hardware validation, merge and release are outside
this gate. Draft PR #30 records final exact-SHA CI.
