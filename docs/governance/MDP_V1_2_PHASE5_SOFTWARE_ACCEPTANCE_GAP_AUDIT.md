# Phase 5 Gates 20–24 — software-only acceptance gap audit

Updated 2026-11-12 for branch `mdp-v1.2/phase5-gates20-24-parallel`, draft PR #45. Gate acceptance remains open under Project Law V1.

## Acceptance review against MDP V1.2

| Gate | Software evidence | Remaining acceptance work |
| --- | --- | --- |
| 20 | `test_ball_contour_position.py` bounds image-to-position error using a known centred raster and a one-pixel rim tolerance. `test_ball_silhouette_range.py` measures error against known 3D centres and rejects partial rims. | Expand raster coverage for noise, occlusion and realistic backgrounds. Verify ELP segmentation and calibration against known references. |
| 21 | `test_offline_marker_runner.py` exercises controlled fiducial pixels, missing markers and untrusted reference displacement. Pose coverage is confined to supported planar geometry with known label correspondence. | Extend ambiguity and non-planar coverage. Validate marker observations and pose against independent ELP reference data. |
| 22 | `test_offline_temporal_evidence.py` covers bounded synthetic frame selection, excessive gaps and ambiguous candidates. Archive diagnostics compare sensor and host intervals independently and check the host trigger boundary. | Document and validate a method that estimates physical contact time against an independent reference. A selected synthetic frame supplies a frame index. |
| 23 | `test_offline_positive_synthetic_image_export.py` checks rendered geometry against known X/Y coordinates and carries frame and session IDs. `test_synthetic_ball_face_contact.py` covers contact geometry. | Verify the physical coordinate reference, centre distance and usable face boundary for actual club models. |
| 24 | `test_offline_frame_quality.py`, `test_offline_temporal_evidence.py` and `test_offline_session_analysis.py` cover unusable frames, bad timing and incomplete archived evidence. Rejected results stay outside point statistics. | Characterize physical measurement uncertainty and false acceptance under ELP noise and occlusion. |
| 26 | `test_offline_impact_demo_socket.py`, the browser session test and portable EXE smoke cover save, reopen and export for synthetic evidence. Archive preserves shot, club, calibration, calculation and quality data. | The capture record identifies the image sequence by hashes and timing. Physical frame retention and retrieval need a validated ELP capture path. Formal closeout awaits user approval. |

## Current acceptance evidence and remaining work

The source is the approved [MDP V1.2](https://github.com/andersdui22/openflight-face-impact/blob/1c36e1b13142a09f17e0daa6d9799341ddbf1eb1/docs/governance/MASTER_DEVELOPMENT_PLAN.md). The Gates below are open. Verify the exact-SHA checks and Windows artifact before submitting this batch for approval.

| Gate | Evidence exercised in software | Outstanding evidence |
| --- | --- | --- |
| 20 | Known sphere/raster positions with one-pixel tolerance, noisy gradient, clipped rim and competing bright components. | ELP recordings with labelled ball positions and representative reflections, blur and occlusion. |
| 21 | Labelled fiducial pipeline, pose ambiguity and incomplete or extra marker rejection. | Physical landmark association and observability against a known club pose. The current supported model is planar. |
| 22 | Independent clock continuity, bounded frame selection and explicit rejection of USB host-clock aliases. | Contact-time estimator and independent timing reference. Frame selection only identifies a candidate image. |
| 23 | Known geometry, polygon boundaries, coordinates, display distance from synthetic origin and image-to-export regression. | Validate physical face origin, geometry and coordinates against an independent reference. |
| 24 | Fail-closed preflight, ambiguous/invalid observations, rejected coordinates withheld, invalid records excluded from calculations. | Physical uncertainty, repeatability and false-acceptance rates. |
| 26 | Repeated shots are saved separately. A retried request is idempotent. Archive reopens after multiple process launches and exports accepted and rejected records with provenance. | Retest archive reopening with this EXE on the user's PC. Retention of real camera frames is pending the ELP acquisition path. |
| 27 | Per-club filtering, coincident point counts, mean and population spread refreshed from persisted records, with exported values checked independently. | Physical sample analysis after an independently validated coordinate path exists. |
| 28 | Browser disconnect/reconnect, embedded Python restart, normal and forced-stop Windows scenarios, plus diagnostics for frame quality, timing, calibration and invalid records. | Hardware-specific settings and failure modes remain to be verified with the ELP adapter. |

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
