# Phase 5 Gates 20–24 — authorized parallel read-only startup audit

Status: **OFFLINE IMPLEMENTATION IN PROGRESS; SOFTWARE ACCEPTANCE NOT YET RECORDED** (2026-11-11). This is a scope and evidence record, not Gate acceptance. See the dated status matrix below for the verified current SHA.

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

## Current software evidence matrix — exact SHA `925c1a3f3248c0112ff7708356117fde20b0a9d0` (2026-11-11)

Read-only GitHub PR #45 audit: **Tests, Face Impact foundation, UI, Pylint and Documentation SUCCESS** on this exact SHA; **PR Checks FAILURE** (PR metadata; not waived). Draft PR #45 remains open, unmerged. The positive rendered-image test `tests/test_positive_rendered_capture_impact.py` is included in the passing test suite, but this is only synthetic accuracy against a known constructed scene, not physical measurement accuracy.

| Gate | Implemented and CI-tested offline evidence | Still missing before software-only closeout | Deferred physical evidence | Disposition |
| --- | --- | --- | --- | --- |
| 20 | Grayscale bright-contour extraction, circularity/edge/ambiguity rejection, calibrated-ray sphere estimation and image-derived positive rendered-scene regression | Robust golf-ball identification under realistic background/occlusion, detection coverage and acceptance thresholds; no claim that any bright circular region is a golf ball | Real camera exposure, optics, segmentation and sphere-range accuracy | **OPEN — offline partial** |
| 21 | Labelled planar face-landmark pose estimation, border/ambiguity rejection and projected-landmark positive synthetic regression | **Actual clubface landmark detection from frame pixels is absent**; current pipeline receives caller-supplied face pixels and cannot prove their provenance | Physical clubface observability and pose precision | **OPEN — offline partial** |
| 22 | Single camera owner and bounded capture-buffer/timing guards; explicit selected frame, shot/session identity and frame metadata consistency; multi-frame offline assessment | **Contact instant is not inferred or selected**; a candidate index must be provided; no subframe reconstruction or evidence-based frame ranking | Camera timing/trigger synchronization and actual contact moment | **OPEN — offline partial** |
| 23 | Synthetic planar tangency, bounded polygon contact and regions, explicit no-tangency/outside-face rejection; positive unmocked image-to-impact synthetic regression | End-to-end observed face landmarks and physical face model provenance missing; no measured contact claim | Actual face coordinates and boundary accuracy | **OPEN — offline partial** |
| 24 | Typed fail-closed impact and quality, per-frame and batch audits, rejection matrix, no invented physical uncertainty | **No calibrated uncertainty estimator or defensible statistical confidence**; no automatic selection or physical validity declaration | Measurement uncertainty/repeatability and independent ground truth | **OPEN — offline partial** |

### Software-first completion rule

All **35 Gates** must be developed as far as feasible without physical hardware before any physical testing begins. Offline software completeness and physical acceptance are separate statuses; hardware-dependent evidence is deferred, **not silently accepted**. Do not block authorized independent software development merely because physical validation is deferred. The canonical Master Development Plan V1.2 acceptance criteria remain unavailable in this inspected repository; individual final Gate closeout requires reconciliation with that approved source. No merges, releases, physical tests or PR-check bypass are authorized.

### Next coherent software batch

Prioritize a bounded **image-derived clubface landmark provenance path** and an explicit **offline candidate-frame selection policy** (or documented rejection if unobservable), using the existing camera owner, immutable capture metadata and synthetic tests. Avoid inventing face detections, contact timing, calibrated accuracy or confidence from synthetic data. Implement in one reviewed package with tests and same-SHA CI.

