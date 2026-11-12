# Phase 5 Gates 20–24 — software-only acceptance gap audit

Updated 2026-11-12 for branch `mdp-v1.2/phase5-gates20-24-parallel`, draft PR #45. Gate acceptance remains open under Project Law V1.

## Evidence available

- Gate 20: synthetic bright-contour ball extraction, circularity/ambiguity/border checks and calibrated-ray sphere estimation; synthetic image regressions. Real golf-ball identity remains unproven.
- Gate 21: labelled planar landmark solver, axis-aligned and perspective synthetic face extraction, and controlled fiducial raster observations associated with known reference labels. Physical clubface identification and landmark validation remain open.
- Gate 22: bounded trigger capture, independently validated sensor/host timestamps, offline gap checks and unique synthetic candidate selection. No physically observed contact instant, clock synchronization or subframe inference.
- Gate 23: planar synthetic tangency and face-polygon coordinate calculation, typed region/boundary rejection, provenance-preserving export. No observed physical impact.
- Gate 24: fail-closed typed result quality, batch audit, temporal acceptance and coordinate suppression for rejected evidence. No physically calibrated uncertainty or repeatability estimate.
- `tests/test_offline_positive_synthetic_image_export.py` verifies positive image-to-export with supplied labelled synthetic face pixels. `tests/test_offline_impact_demo_socket.py` adds a successful controlled ball-and-marker raster replay with positive and rejected evidence delivered to one requesting client. The Playwright localhost test exercises the React review, marker and rejected history entry.

## Explicit acceptance gaps and priorities

| Priority | Gate | Required software-only evidence before provisional closeout |
| --- | --- | --- |
| P0 | 20–24 | Exact-SHA CI all required checks green; record result and any environment-only failures distinctly |
| P0 | 20–24 | Recovered the [approved MDP V1.2](https://github.com/andersdui22/openflight-face-impact/blob/1c36e1b13142a09f17e0daa6d9799341ddbf1eb1/docs/governance/MASTER_DEVELOPMENT_PLAN.md). Use its Phase 5 objectives for individual acceptance review. |
| P0 | 23–24 | Positive and rejected synthetic image-to-export regression exists with frame, shot and session identity. Verify browser and Windows mock evidence on the code SHA. |
| P1 | 21 | Extend controlled image evidence for ambiguous, non-planar and unobservable scenes. Unmarked physical recognition remains open. |
| P1 | 22 | Explicit temporal evidence policy: unique geometry is not a contact instant; define offline handoff limits and rejected cases |
| P1 | 20,24 | Expand segmentation/occlusion/noise and batch consistency tests with bounded inputs and fail-closed results |
| Deferred | 20–24 | ELP OV9281 physical acquisition, exposure timing, actual ball/face observability, ground-truth impact, calibration and uncertainty |

## Exit criteria and phase transition

- Mark each Gate **software-complete / physical-verification-deferred** only when its documented software criteria and exact-SHA tests pass and the user approves technical closeout under Project Law V1.
- If a software criterion cannot be fulfilled without physical evidence, record it as an explicit limitation rather than pretending it passed.
- Gates 25–28 cover integration and user functions. Gates 29–30 require physical testing and an independent reference. The software preparation and its current evidence are recorded in `PHASE6_SOFTWARE_FIRST_START.md`.
- Preserve one camera owner, no upstream/ConnectorNext changes, no physical tests, no merge/release without separate approval.

## CI provenance

The preceding commit `d99ea571e9476276278152113f1f8905a0758b52` passed all six GitHub workflows. On writing this audit, `fa0972ccc386beee9266f9b20bdc03981a93f3e5` workflows were queued; **do not inherit** the previous SHA's success.
