# Phase 5 Gates 20–24 — software-only acceptance gap audit

Date: 2026-11-11. Scope: current branch `mdp-v1.2/phase5-gates20-24-parallel`, draft PR #45. This is **not** a Gate acceptance record or approval to merge/release.

## Evidence available

- Gate 20: synthetic bright-contour ball extraction, circularity/ambiguity/border checks and calibrated-ray sphere estimation; synthetic image regressions. Real golf-ball identity remains unproven.
- Gate 21: labelled planar landmark solver, axis-aligned and optional perspective bright synthetic face extraction, image-to-pose regression. No general real clubface identification, physical landmark validation or arbitrary orientation guarantee.
- Gate 22: bounded trigger capture, independently validated sensor/host timestamps, offline gap checks and unique synthetic candidate selection. No physically observed contact instant, clock synchronization or subframe inference.
- Gate 23: planar synthetic tangency and face-polygon coordinate calculation, typed region/boundary rejection, provenance-preserving export. No observed physical impact.
- Gate 24: fail-closed typed result quality, batch audit, temporal acceptance and coordinate suppression for rejected evidence. No physically calibrated uncertainty or repeatability estimate.
- End-to-end rejection integration: `offline_impact_handoff.py` reaudits a real synthetic image-derived batch, validates timing, and exports only admissible synthetic evidence. Its current integration tests exercise the **rejection path**, not a successful physical impact.

## Explicit acceptance gaps and priorities

| Priority | Gate | Required software-only evidence before provisional closeout |
| --- | --- | --- |
| P0 | 20–24 | Exact-SHA CI all required checks green; record result and any environment-only failures distinctly |
| P0 | 20–24 | Recover and reconcile the canonical approved Master Development Plan V1.2 acceptance criteria, absent from inspected repository; do not substitute this audit for the canonical plan |
| P0 | 23–24 | Positive, unmocked image-to-batch-to-timing-to-export **synthetic** regression with explicit frame/session identity and rejection counterparts; **still open** (existing integration only exercises rejection) |
| P1 | 21 | Demonstrate synthetic face-corner detection provenance and rejection of ambiguous/non-planar/unobservable scenes; no real clubface claim |
| P1 | 22 | Explicit temporal evidence policy: unique geometry is not a contact instant; define offline handoff limits and rejected cases |
| P1 | 20,24 | Expand segmentation/occlusion/noise and batch consistency tests with bounded inputs and fail-closed results |
| Deferred | 20–24 | ELP OV9281 physical acquisition, exposure timing, actual ball/face observability, ground-truth impact, calibration and uncertainty |

## Exit criteria and phase transition

- Mark each Gate **software-complete / physical-verification-deferred** only when its documented software criteria and exact-SHA tests pass and the user approves technical closeout under Project Law V1.
- If a software criterion cannot be fulfilled without physical evidence, record it as an explicit limitation rather than pretending it passed.
- Independent development of Gates 25–30 may be planned and, subject to the applicable authorization, developed in a separate branch without silently closing Gates 20–24.
- Preserve one camera owner, no upstream/ConnectorNext changes, no physical tests, no merge/release without separate approval.

## CI provenance

The preceding commit `d99ea571e9476276278152113f1f8905a0758b52` passed all six GitHub workflows. On writing this audit, `fa0972ccc386beee9266f9b20bdc03981a93f3e5` workflows were queued; **do not inherit** the previous SHA's success.
