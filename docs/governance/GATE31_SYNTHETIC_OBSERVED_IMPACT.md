# Gate 31 synthetic Face Impact from supplied image observations

Anders approved this offline contact integration on 2026-11-09. Gate 30
`3f91831bd62bd208b131559aa19cac56c41f85f5` is the base. Its draft PR
recorded seven successful workflows on that SHA. Physical tests remain deferred.

## Existing components and decision

Gate 28 converts pixels to calibrated camera rays, Gate 29 estimates a sphere
centre from a supplied full rim and explicit radius, and Gate 30 estimates a
face-local pose from labelled planar points. Gate 18 already classifies ball
contact against a finite synthetic face. The new entry point composes these
functions and passes the camera frame as the existing geometry's world frame.
No additional sphere, pose or contact solver is needed.

## Input contract and limits

The caller supplies ball rim pixels, paired face-local landmarks and pixels,
an explicit face polygon and ball radius in millimetres, image dimensions and
fit thresholds. The two pixel sets must describe the same candidate instant
and calibrated camera mode. The face polygon and landmarks must share their
heel-to-toe, bottom-to-top origin and scale. The software does not establish
those conditions from the pixels and does not choose the contact frame.

The caller also supplies a normal-direction tangency tolerance in millimetres.
The integration tests use 0.01 mm to accommodate floating-point inversion and
pose solving on generated exact data; this number is not a physical accuracy
or measurement-uncertainty estimate. Sphere and face fit limits remain in
radians and pixels respectively. All invalid observations and geometry return
an existing rejection status with no impact coordinates. A sphere separated
from the plane returns `no_tangency`; a tangent point outside the supplied
polygon returns `outside_face`.

## Verification and unknowns

Tests independently generate a known sphere, tangent silhouette rays, a
rotated/transformed face, polygon and distorted image points. They require
signed heel/toe and vertical millimetres within 0.01 mm of the synthetic
truth, then check separation, polygon exclusion, partial rim, ambiguous face
pose, mismatched image size and invalid polygon. They exercise the existing
components together without hardware. Draft PR #31 records the final SHA and
CI evidence.

Real edge and landmark detection, simultaneous capture, calibration quality,
contact timing, Windows runtime integration and physical Face Impact accuracy
remain unverified. No physical Golden baseline has been designated.
