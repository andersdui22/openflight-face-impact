# Phase 0 source audit, 2026-11-08

The [official OpenFlight source](https://github.com/open-flight/openflight)
default branch is `main`, HEAD
`a3ab081a8abff71fd344d4fd782412d624b99f3f`. This local preparation clone
contains the upstream history and starts at that commit. The upstream check
runs were green at audit time, but they do not prove Windows or physical camera
behavior. Phase 0 modified no upstream files.

## Implemented in official main

- Flask/Flask-SocketIO backend (`src/openflight/server.py`) and existing
  React/TypeScript UI plus Electron URL kiosk shell (`ui/`). Electron does not
  start or package the Python service.
- Pi Picamera2/libcamera capture (`src/openflight/camera/capture_runtime.py`),
  with synchronized frames, ring buffer, trigger, preview/replay and optional
  camera analysis. The Pi OV9281 CSI setup is not ELP USB Windows support.
- Original Linux/macOS resolver settings in `pyproject.toml` and Linux GitHub
  Actions for backend/UI. No Windows runtime verification in official main.

## Experimental public source, not merged into the baseline

- [PR #245](https://github.com/open-flight/openflight/pull/245), head
  `c0da896d141c4b10e1db100d16b03403b406a7c2`: club mesh, projection and
  teed-ball localization; no shot wiring. Contributor reports 21/22 captures
  for ball localization; this project has not reproduced the reference data.
- [PR #250](https://github.com/open-flight/openflight/pull/250), head
  `8d244e25e41764bdeb5665a812af40ccf2e37b16`: stacked pose estimation,
  scores and delivered-angle calculation. Its author explicitly reports no
  physical orientation or impact-location accuracy figure. One PR-quality
  check was returned; functional CI for this exact head is unverified.
- [Public fork checkpoint](https://github.com/HarjotDhanota/openflight/tree/ea95a64329e5bbea52f901e3badb1cb07995a6fc)
  `ea95a64329e5bbea52f901e3badb1cb07995a6fc`: Face Impact schematic UI,
  asynchronous post-shot worker, optics, range evidence and category geometry.
  It is an explicit unfinished archival checkpoint without returned CI checks.
  Newer code can estimate resting-ball range from angular ball size with a
  calibrated camera, despite older documentation saying radar range is always
  needed. The output remains `experimental_unqualified`; this is no proof of
  physically measured clubhead depth or strike.

## Missing or unverified for the one-camera Windows objective

ELP OV9281 USB mode/exposure/timestamp support, Windows capture adapter,
camera-only session and shot trigger, measured intrinsics, legally usable
actual-club meshes, unambiguous moving-head pose, first touch, independent
impact ground truth, repeated-shot reliability, and integrated clean-Windows
packaging. None has a Golden physical baseline. A known ball diameter supplies
a possible scale anchor, but motion blur, occlusion and pose ambiguity can
prevent a readable strike. No millimetre accuracy is promised.

## Dependencies, provenance and test distinction

The intended data path is USB camera → one capture owner/ring → calibrated
frames and ball/club observations → conditional geometry/pose/impact worker →
shot identity and uncertainty → existing backend API → original React UI.
Acquisition must remain responsive while the worker processes a shot.

The experimental 690CB STL and normalized NPZ are local research assets with
no redistribution clearance. A retired driver scene is not a valid fallback.
Source presence, contributor claims, CI, simulation and physical measurements
are separate kinds of evidence. This gate changes none of the application
modules; see `CANDIDATES.md` and `THIRD_PARTY_NOTICES.md` for admission limits.
