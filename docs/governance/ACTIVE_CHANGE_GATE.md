# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 11

Title: Camera-only synthetic 3D mesh projection
State: ACTIVE — user explicitly approved "Godkendt" after Gate 11 scope proposal (2026-11-08).
Project Law: V1 unchanged.
Working branch: `gate11/camera-only-mesh-projection`.
Base: Gate 10 HEAD `3b4eca7149dbce637ac66c33a24f14c39bdc01d6`, six of six same-SHA CI successful; draft PR #10 unmerged.

## Authorized scope

Narrowly reuse/adapt OpenFlight experimental 3D triangle mesh projection and rasterization for deterministic synthetic fixtures. Accept explicit camera intrinsics/extrinsics rather than original fixed radar/rig geometry. Add synthetic tests for coordinates, orientation, and invalid inputs. Preserve upstream provenance and AGPL notices; do not import or distribute restricted 690CB assets.

## Exclusions and stop conditions

No real pose fit, real face detection, physical ELP camera test, radar dependency, face impact millimetres, UI redesign, merge, release or Golden baseline. Reject ambiguous or invalid calibration and any model requiring unapproved redistribution. Stop on unexpected CI failures or upstream dependency incompatibility.
