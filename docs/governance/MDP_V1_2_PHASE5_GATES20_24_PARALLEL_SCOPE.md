# Phase 5 Gates 20–24 — authorized parallel read-only startup audit

Status: **READ-ONLY AUDIT COMPLETE; IMPLEMENTATION NOT YET STARTED** (2026-11-11). This is a scope and evidence record, not Gate acceptance.

## Authorization and immutable baseline

- User explicitly approved parallel development of Gates 20–24 under Project Law V1, with read-only audit first, automated tests and CI. All physical tests are deferred until development of all 35 Gates; merge and release require separate authorization.
- Repository: `andersdui22/openflight-face-impact`.
- New branch: `mdp-v1.2/phase5-gates20-24-parallel`, created from exact Phase 4 integration SHA `fcda0ff666eb6c39f90777947d8b70a55a172492`. Draft Phase 4 PR #44 remains open and unmerged. No changes to main, upstream or ConnectorNext.
- Verified at startup: the preceding code SHA `8e44a8584d95dfa6ea5229e9af5072c862fcfb60` passed six technical workflows. The Phase 4 documentation HEAD `fcda0ff6` still had some CI runs in progress at audit time; its PR Checks failed under the user-deferred screenshot requirement. Do not inherit prior SHA's checks as proof of this branch's new commits.
- Read Project Law V1, `ACTIVE_CHANGE_GATE.md`, `BASELINES.md`, `CANDIDATES.md`, `HANDOFF.md`, Phase 4 scope and GitHub repository tree at the immutable base. The governance files contain historical Gate 13–15 snapshots; the current user authorization supersedes historical *permission status* only, not technical evidence or Law requirements.
- Canonical Master Development Plan V1.2 file was **not located in the inspected repository tree**. Gate 20–24 names below are conversation-derived and must be reconciled with the canonical approved plan before final individual acceptance.

## Gate boundaries and provisional acceptance

| Gate | Conversation-derived topic | Offline scope and acceptance direction |
| --- | --- | --- |
| 20 | Ball detection, silhouette and observation quality | Reuse existing silhouette/ray geometry. Reject missing, degenerate, clipped or ambiguous observations; provenance and quality must be explicit. No invented ball location. |
| 21 | Clubface detection and 3D pose | Reuse labelled planar landmark solver and synthetic pose observability. Reject non-observable pose and unsupported curved geometry; do not infer real pose from a generic club category. |
| 22 | Contact instant and temporal reconstruction | Audit single camera owner, bounded shot/session frame buffers, trigger semantics and available timestamps. Never label host-arrival timestamps as sensor exposure time. Do not invent subframe contact. |
| 23 | Impact coordinates, centre distance and face boundary | Reuse synthetic contact pipeline and Gate 17 planar reference conventions; keep out-of-face and no-tangency outcomes explicit; no coordinates for rejected results. |
| 24 | Uncertainty, quality control and rejection | Carry observable uncertainty and rejection causes through result contracts. No physical millimetre accuracy claim from offline synthetic tests. |

## Reuse audit and evidence limits

- `src/openflight/camera/ball_silhouette_range.py` already estimates a candidate sphere centre from at least five calibrated silhouette rays, explicit radius and residual threshold; it does not detect pixels or prove physical depth accuracy.
- `src/openflight/camera/calibrated_rays.py` converts calibrated pixels to optical rays; do not duplicate.
- `src/openflight/camera/synthetic_face_landmark_pose.py` solves a labelled planar face pose using explicit calibration and candidate ambiguity thresholds. Its synthetic-only scope is not verified physical pose.
- `src/openflight/camera/synthetic_pose_observability.py` scores bounded candidate poses and rejects ambiguous silhouettes; not a real clubface detector.
- `src/openflight/camera/synthetic_observed_impact.py` composes supplied synthetic ball edges and face landmarks; it **does not determine contact time**.
- `src/openflight/camera/synthetic_impact_pipeline.py` and `synthetic_impact_socket.py` provide synthetic-only contact results and explicit outside-face/no-tangency rejections. Do not require physical calibration to run this synthetic demo.
- Phase 4 optics/profile/club binding checks are offline-only. No physical measurement publication endpoint has been established. Do not connect new guards to unrelated radar/ballistics handling.
- Candidate registry records upstream experimental geometry and restricted 690CB assets; no unapproved asset import or assumption of license admissibility.
- Existing camera acquisition and buffer must retain one owner; no new receive loop.

## Work sequencing and stop conditions

1. Verify source/tests and decide minimal reusable interfaces for Gate 20 observation quality and Gate 21 pose ambiguity; develop independently where possible.
2. Audit Gate 22 timing source, shot/session ownership and buffer provenance before modifying any temporal reconstruction.
3. Build Gate 23 on verified coordinate contracts and explicit finite face boundaries; build Gate 24 on typed outcomes from Gates 20–23.
4. Keep commits focused with corresponding synthetic/offline tests; verify CI at the exact SHA. Separate technical acceptance of each Gate from deferred physical acceptance.
5. Stop on a material contradiction with canonical plan, unavailable license/provenance, out-of-scope behavior or unverified physical assumptions. No physical tests, merge, release, fabricated screenshot, PR check bypass or claimed measured impact accuracy.

**Next implementation candidate:** a bounded pure Gate 20 observation-quality validator around supplied ball silhouette samples, *not* a second detector or camera reader. Audit its current tests and the existing `ball_silhouette_range` contract before coding.
