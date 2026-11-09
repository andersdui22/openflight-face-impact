# Gate 29 synthetic ball position from silhouette rays

Anders approved the camera-only synthetic sphere estimate on 2026-11-09.
Gate 28 `60a4232463aed9352cfe7a631394ef6ff26a166f` is the base.
Physical tests remain deferred under Gate 26.

## Source and reuse

The existing sphere-to-face routine requires the ball centre as input.
The experimental OpenFlight [resting-ball range](https://github.com/HarjotDhanota/openflight/blob/ea95a64329e5bbea52f901e3badb1cb07995a6fc/src/openflight/camera/resting_ball_range.py)
derives lens distance as radius divided by sine of the angular half diameter.
Gate 29 reuses this relation with attribution. It fits an axis and angular
radius from multiple Gate 28 silhouette rays instead of assuming a horizontal
diameter and a supplied centre pixel. Results stay in the camera frame.

## Contract and evidence

Input consists of at least five distinct forward unit rays to a sphere rim,
an explicit ball radius in millimetres, and an angular residual limit in
radians. The fit uses the fact that tangent directions make a constant
angle to the centre direction. Output is the centre in right/down/forward
camera millimetres, optical range, angular radius and worst angular residual.

The solver rejects inconsistent rays, an angular size below resolution
of the chosen residual budget, and rim samples whose largest azimuth gap
is at least half a revolution. This deliberately excludes a short arc even
if a mathematical circle can fit it. The residual budget and coverage rule
are software acceptance checks. A low residual is not a physical accuracy
or uncertainty estimate.

Tests generate tangent points on virtual spheres with independently known
centres and project them through synthetic optics before Gate 28 inversion.
They cover distances from 260 mm to over 1.35 m, off-axis positions, small
observation perturbations, partial rims, disagreement, unresolved size and
invalid inputs. No real detector, physical ball dimensions, camera capture,
contact integration or runtime changes. Draft PR #29 records final exact-SHA CI.
