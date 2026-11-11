# PHASE 5 GATE 20 RESULT-CONTRACT HARDENING (2026-11-11)

- Read-only startup audit of draft PR #45 at `bbb8a5f7a14da70ea975e1fd9f60a931fbe76b40`: all five technical workflows SUCCESS; PR Checks FAILURE due title and required PR-description sections. Source and tests inspected before editing.
- Gate 20: reject invalid/nonfinite/boolean or inconsistent range, angular radius and residual in immutable BallSilhouettePosition results. Tests cover malformed scalar diagnostics and valid contract; no physical accuracy claim.
- Atomic batch changes source, tests and handoff in one commit. CI for this new HEAD pending; do not infer results from preceding SHA. Gate 20–24 OPEN. No hardware tests, merges, releases, or PR check bypass.

---

# PHASE 5 GATE 22 CI CONTRACT FIX (2026-11-11)

- Read-only audit at `2d1fab4cd3502319790c3c7c3c40f2db17e86869`: Documentation, Pylint, Face Impact foundation and UI passed; Tests failed 3 assertions on changed error wording. PR Checks still fail title/description. CI logs show all 3 failures expect substring `missing capture identity` while the new stricter identity validator returned `missing or invalid capture identity`.
- This atomic batch preserves existing diagnostic contract `missing capture identity` while retaining the new requirement that shot_id and session_id be nonblank strings. No test weakening, no hardware changes. All source/tests from previous batch remain.
- CI for new SHA must be checked; gates 20–24 remain OPEN. No physical tests, merge or release.

---

# PHASE 5 GATE 22 IDENTITY VALIDATION BATCH (2026-11-11)

- Read-only startup audit of draft PR #45, head `b7483af87ba55972df97239bfbcf736376e85af7`: Tests, Pylint, Face Impact foundation, UI and Documentation all SUCCESS. PR Checks FAILURE: title and missing required description headings.
- Gate 22 hardening: require both shot_id and session_id to be nonblank strings, not merely truthy values; reject malformed integers, booleans, lists and whitespace-only identity. New focused regression tests. This protects offline provenance validation only; it does not infer physical contact or bind supplied pixels to a capture frame.
- Changes to source, tests and handoff committed atomically once to minimize GitHub CI. New commit CI must be verified before claiming acceptance. PR metadata still requires edit; no tool currently available for PR edits.
- All Gates 20–24 OPEN; physical testing deferred until all 35 Gates developed. No merges/releases.

---

# PHASE 5 GATE 22 BATCH REGRESSION CHECKPOINT (2026-11-11)

- CI on `ae78a6991a5c239084e8e092087eec9dc2943fdb`: **all five technical workflows passed** (Tests, Pylint, Face Impact foundation, UI, Documentation). PR Checks failed exclusively on conventional title and required PR-description sections. Do not claim PR Checks green.
- This batch adds synthetic integration regression tests for invalid capture session identity, nonmonotonic host clock, unbracketed trigger and omitted candidate index. Every rejection must expose no impact coordinates or region labels. No actual image-to-frame correspondence verification and no contact timing inference.
- PR metadata still needs a compliant title and required headings; no connected PR-edit tool available. Do not change CI rules or bypass checks. CI on this batch's new SHA is pending.
- User-approved batched development: keep code, tests and handoff in same Git tree commit to reduce redundant CI. Gates 20–24 remain OPEN, no physical tests until all 35 Gates developed, no merge/release.

---

# PHASE 5 BATCH CI FAILURE AND FIX (2026-11-11)

- Read-only audit of draft PR #45 at `d6b701f853a6ee35710c30ced2829712458c7109`: Documentation, Pylint and Face Impact foundation passed; Tests FAILED on Python 3.11 (2627 passed, 1 failed, 7 skipped); UI still in progress at audit. PR Checks failed on nonconventional PR title and missing required PR description sections, NOT on screenshot check according to job list.
- Exact failure: `test_mismatched_calibration_size_is_rejected` expected `dimensions`, but newly inserted Gate 20 contour border validation rejected the observation first. This batch fixes fail-closed validation ordering: `calculate_synthetic_observed_impact` now rejects `image_size != calibration.image_size` before contour inspection, with explicit dimensions message. Regression test also supplies a clipped contour and mismatched dimensions to lock precedence.
- PR metadata must be updated separately (title conventional, description headings `Why was this required?`, `Automated tests`, `Manual (human) testing`), without claiming manual testing. GitHub tool surface currently has no PR edit action; do not bypass governance or invent screenshots.
- Source, regression test and handoff committed together in one Git tree/ref update to minimize CI. Recheck CI on resulting HEAD. Gates 20–24 OPEN; no physical testing, merge or release.

---

# PHASE 5 BATCH DEVELOPMENT CHECKPOINT (2026-11-11)

- User approved batching changes to reduce GitHub Actions cost. This checkpoint is included in the **same Git tree commit** as source and tests, rather than a separate handoff push.
- Batch integrates optional Gate 22 timing provenance into `calculate_synthetic_observed_impact`: caller can supply a `TriggeredCapture` and explicit `candidate_frame_index`; invalid timing/identity/index rejects with `INVALID_GEOMETRY` and no impact coordinates. Existing synthetic-only callers remain supported. This is **NOT** frame-image correspondence verification, a physical contact detector, or a claim that the trigger equals impact time. No second camera acquisition owner.
- Synthetic integration tests cover accepted explicit candidate, out-of-range candidate, and missing capture. Source/test/handoff committed together. CI must be checked at resulting HEAD; do not claim green until verified.
- Gates 20–24 remain OPEN. No physical testing until 35 Gates, no merge or release without separate approval.
- Next: same-SHA CI, correct failures as one batch, then continue quality/uncertainty integration. Prefer single Git tree/commit/ref update per coherent batch.

---

# PHASE 5 GATE 20 OBSERVED IMPACT INTEGRATION (2026-11-11)

- Read-only audit of PR #45 at `64e1a674f685898b4331a4301ac84f8d5213ec0c`: draft, technical workflows queued at time of check; no latest-SHA CI success claimed.
- Commit `8b67a41407edc4e99851151cfc5789b259612b4d`: `calculate_synthetic_observed_impact` now calls `validate_ball_contour_pixels` before calibrated ray inversion. Optional explicit `ball_border_margin_px=0.0` maintains existing caller compatibility. Invalid or clipped contours yield existing `INVALID_GEOMETRY` rejection with no impact coordinates. This is synthetic/offline only.
- Commit `bafabf36ec3e01887435e78d4d893f616fbf00df`: synthetic observed-impact tests check rejection for border clipping and accepted known contact with positive margin.
- Important: No actual image contour detector, no physical contact timing, no ELP hardware test, no release/merge. Gate 20–24 remain OPEN. Latest code has NOT been verified against same-SHA CI; inspect and fix technical failures. Reassess whether optional zero margin is sufficient for eventual physical observations (requires evidence).
- Next: exact-SHA CI, then Gate 21/22/23/24 synthetic end-to-end gating and quality contract; avoid asserting physical accuracy. Handoff update advances SHA.

---

# PHASE 5 GATE 20 IMAGE-DOMAIN CONTOUR QUALITY (2026-11-11)

- Draft PR #45 audited at `9d57a2484e0d94543989c7c332f3bb10bf9e50d4`: Documentation passed; foundation and Pylint in progress; Tests, UI and PR Checks queued. Prior `6c741f57...` had Documentation, Pylint, foundation green; Tests/UI in progress; PR Checks failed. **Do not claim latest SHA CI green.**
- Gate 20 new standalone offline contour-quality validator `src/openflight/camera/ball_contour_quality.py` at commit `cd1be109138974fe97f6f5bf773b7bf4e0233801`: checks image dimensions, explicit safe border margin, >=5 finite distinct pixel pairs, clipping; returns a defensive copy. This does **not** detect contours, infer ball identity or assert physical accuracy.
- Gate 20 tests `tests/test_ball_contour_quality.py` at `82494302338c5fc2bf4d9728fe033947401fbc6d`: valid copy, bad shapes/nonfinite/duplicate samples, border clipping, invalid image/margin.
- This is standalone; next step is to integrate into the synthetic observed-impact path with an explicit configurable margin, and verify existing call sites/tests before modifying signatures. Calibrated ray solver already checks ray coverage and consistency separately.
- Gate 22 explicit frame-index and provenance checks, Gate 21 pose quality, Gates 23–24 impact result invariants remain in same branch; see previous handoff entries. Recheck exact-SHA CI and resolve technical failures. No physical tests, merges or releases.

---

# PHASE 5 GATE 22 CANDIDATE FRAME CHECKPOINT (2026-11-11)

- PR #45 remains draft/unmerged. Last read-only audit of `6c741f579fba1bd8d2359687cb9b886368635be8`: Pylint and Documentation passed; foundation in progress; Tests, UI and PR Checks queued. A much older SHA `70093cfae191068f4eb7056f5b43e4c65e575e9b` had all technical workflows green, with PR Checks red (deferred screenshots). **No same-SHA green claim for latest changes.**
- Gate 22 commit `b912d31a3e1bf237bb5cf2890c6f7aebfad576c7`: `validate_candidate_frame_index(capture, candidate_index)` now requires valid capture timing/identity and an explicitly supplied bounded frame index. It does NOT infer the physical impact instant from trigger or timestamps. Test commit `e051dc75e39eebe2f2a0e72097cbd385fb1496c8` checks accepted indices, invalid indices and rejected provenance.
- This is an offline contract helper only, **not yet wired into impact calculation or live publication**. The selected candidate remains a hypothesis, not verified physical contact.
- Next: verify CI on new HEAD, check Pylint and tests, then continue Gate 20 contour quality and Gate 21/23/24 integration. No physical tests until all 35 Gates, no merge/release without authorization. Handoff commit advances HEAD.

---

# PHASE 5 GATE 22 RING INTEGRATION TEST CHECKPOINT (2026-11-11)

- PR #45 read-only audit: HEAD `85e87a96545adbb117f966907ea17a216405085b`, draft, unmerged. All six PR workflows were **queued** when checked, including Tests, Pylint, UI, Documentation, foundation and PR Checks. **No same-SHA pass has been verified.**
- Commit `872a3ff4b19495ced1e2f225ef9a05801ca5ec39` adds an offline Gate 22 regression test feeding actual `TriggeredFrameBuffer` frames, firing a deterministic host trigger, consuming `TriggeredCapture`, checking shot/session identity and passing it to `assess_trigger_timing`. Also tests rejection when trigger precedes the last pre-frame host timestamp. No hardware involved.
- **Important:** This integration test only exercises synthetic frame metadata and the existing ring buffer; no physical contact timestamp is inferred. Gate 22 validator is still standalone and not connected to real measurement publication.
- NEXT: Recheck GitHub CI on latest HEAD after this handoff commit; avoid repeatedly pushing documentation-only commits if CI is queued. If technical CI fails, inspect job logs and fix. Also inspect existing `SyntheticImpactResult` constructors for Gate 23–24 contract compatibility and reconcile exact MDP V1.2 Gate definitions before closeout. Continue approved parallel Gates 20–24, no merge/release/physical testing.

---

# PHASE 5 GATE 22 OFFLINE TIMING PROVENANCE (2026-11-11)

- Draft PR #45 remains the approved Phase 5 work surface; no merge/release/physical tests.
- Read `triggered_buffer.py`, `capture_runtime.py` and `test_camera_triggered_buffer.py`. Existing `TriggeredCapture` has distinct sensor timestamps, host timestamps, host trigger time, shot/session IDs and pre/post frame boundary. This is a pre-existing camera ring, not proof of actual impact instant.
- Gate 22 implementation commit `e2d7859f14f9c7ad985440f5f6cb97828c99c89c`: new pure `src/openflight/camera/trigger_timing_quality.py` rejects missing pre/post frames, bad/missing shot/session identity, invalid/nonmonotonic sensor or host clocks and host triggers not bracketed by the pre/post host timestamps. It **does not** compare unrelated sensor and host clock epochs, infer contact time or create a second acquisition owner.
- Gate 22 synthetic tests commit `94ff3f3b89b3aed21895b0d72fc6c6e2eb0d7042`: valid and rejected capture provenance, nonmonotonic clocks and distinct clock origins.
- This is an **offline validator not yet wired to a physical publication path**. It is not hardware calibration or exposure-time verification.
- The latest new commit's CI is not verified. Inspect exact-SHA workflow outcomes and fix failures; consider whether the host trigger bracketing rule is too strict for a real asynchronous trigger before integrating (keep it a conservative rejection until justified).
- Gate 20, 21, 23 and 24 changes are documented in preceding handoff sections. Recheck their CI and result-constructor compatibility. Current handoff edit advances HEAD.

---

# PHASE 5 PARALLEL GATES 21, 23, 24 — CHECKPOINT (2026-11-11)

- Branch `mdp-v1.2/phase5-gates20-24-parallel`, draft PR #45 https://github.com/andersdui22/openflight-face-impact/pull/45 (unmerged). At previous SHA `70093cfae191068f4eb7056f5b43e4c65e575e9b`, Documentation, foundation and Pylint succeeded, UI and Tests were still in progress, and PR Checks failed on the deferred screenshot policy. These are NOT checks on the new commits below.
- **Gate 21** code `5c91e524e274b037267954e9dfdf8d36300b22bf`: existing synthetic planar pose estimator rejects malformed RMS/margin thresholds before OpenCV. Tests `01f09cc1b3d4f893b0d0a7bb63b977962a07dd0b`: invalid scalar/bool/array/nonfinite thresholds.
- **Gates 23–24** code `7e6002af00663ee2af776ac530cf9ffdc01c7621`: synthetic impact result contract enforces finite coordinates and populated region labels for accepted results, and forbids coordinates/regions on rejected results, requiring an explicit rejection reason. Tests `061a6ee3bbff102af4ef6b0953c87536f029a900`: contradictory-result regressions.
- **Gate 20** earlier code and tests remain on the branch; Gate 22 timing/trigger provenance audit is still pending.
- All new code is synthetic/offline only; no physical camera tests, merge, release, new camera receive owner, or claims of physical pose/impact accuracy.
- **Immediate next step:** verify the new exact-SHA technical CI; inspect and correct failures. Audit all existing `SyntheticImpactResult` constructors for compatibility with new fail-closed invariant. Then audit Gate 22 timestamp source and shot/session ownership. Update this handoff after meaningful milestones. This handoff commit advances SHA, so re-fetch remote HEAD.

---

# PHASE 5 GATE 20 IMMUTABILITY CHECKPOINT (2026-11-11)

- Draft PR #45 remains unmerged. At last observed PR HEAD `7c2b89af1cf96d27cb55e2f97d4465e23c331f83`, Documentation succeeded, other technical CI workflows were in progress, and PR Checks failed under the previously deferred screenshot requirement. Do not claim technical CI passed.
- Gate 20 commit `a155ae8b54fcd13b0e16aedf07f361a227aa80e2`: `BallSilhouettePosition` now validates, copies and write-protects its camera XYZ result array to prevent caller mutation/aliasing of an accepted observation.
- Gate 20 commit `9d913ecfd1bb8f9d94594b454daf722de0008d9e`: regression tests for write protection, caller-array aliasing and invalid result coordinates.
- **New commits require same-SHA CI verification**. Next: inspect tests/Pylint on newest head and fix introduced failures. Continue only within approved Gates 20–24; no physical ELP tests, merge or release.
- This handoff edit advances HEAD again; always fetch current GitHub HEAD and CI before continuing.

---

# PHASE 5 PR AND CI CHECKPOINT (2026-11-11)

- Created **draft PR #45**: https://github.com/andersdui22/openflight-face-impact/pull/45, head `mdp-v1.2/phase5-gates20-24-parallel`, base `mdp-v1.2/phase4-gates17-19-parallel`. No merge/release.
- PR creation triggered GitHub Actions on SHA `d3992511719458bec1d09ca5689cff4f963ad9be`. At observation, Tests, Pylint, UI, Documentation and PR Checks were **in progress**; Face Impact foundation **queued**. No successful same-SHA result yet. Recheck latest HEAD after this handoff commit and verify **its** CI.
- Gate 20 source and regression test commits: `105e99ec`, `ff801f0e`. Only strict validation of supplied radius and angular residual budget has changed; no physical ball detector or camera reader added.
- Next: inspect failing CI jobs if any, fix within scope, then continue bounded Gate 20 observation-quality and Gate 21 pose-validation work. Keep this file current after milestones.

---

# PHASE 5 IMPLEMENTATION UPDATE — GATE 20 (2026-11-11)

- Verified Phase 5 branch `mdp-v1.2/phase5-gates20-24-parallel` at prior handoff SHA `2d388f87537ab6216ece5b1b61b84043d9f48822`; no PR-triggered workflow runs were returned for that SHA (not a pass).
- Read `src/openflight/camera/ball_silhouette_range.py` and `tests/test_ball_silhouette_range.py`. Reused the existing sphere/rim estimator; **did not** add a second camera owner or detector.
- Gate 20 code commit `105e99ec15159e019c23e4aa35f89b11e95fc336`: fail-closed scalar type checking for radius and angular residual budget, avoiding exceptions or ambiguous NumPy array truth values.
- Gate 20 test commit `ff801f0e7f1361013e137e7927d81a766b0f842e`: malformed scalar/radius/budget regression cases. These are synthetic hardware-free tests, not physical accuracy validation.
- **CI for `ff801f0e` and this handoff's newer SHA has NOT been verified**. Next: check same-SHA CI; if absent because no Phase 5 PR exists, create a draft PR on the approved Phase 5 branch with the proper stacked base, then verify checks. Fix any introduced failures.
- Continue Gates 20–24 within user-approved scope. All physical testing deferred until after development of 35 Gates; no merge/release/screenshot bypass.
- Read the current full handoff and `MDP_V1_2_PHASE5_GATES20_24_PARALLEL_SCOPE.md` below before resuming.

---

# CURRENT HANDOFF — PHASE 5 GATES 20–24 (2026-11-11)

**READ THIS FIRST.** This section supersedes earlier status snapshots below. GitHub is authoritative for current HEAD, CI, PRs and files. Re-audit before any code change; this handoff is a dated snapshot.

## Mission and authorization
- Project: standalone Windows **OpenFlight Face Impact** using one **ELP OV9281 USB camera**; reuse existing Python/OpenCV and React/Electron code. No ConnectorNext, MLM2PRO, Bluetooth, radar, GSPro or upstream OpenFlight edits.
- Law: `docs/governance/PROJECT_LAW.md` **Project Law V1**. The user explicitly approved **parallel development of Phase 5 Gates 20–24**, starting with read-only audit, then hardware-free tests and CI. Physical testing is postponed until development of **all 35 Gates**. **No merge, release or physical testing** without separate authorization. UI screenshots are deferred, **not waived**; never fake or bypass PR Checks.
- Working repository: `andersdui22/openflight-face-impact`. Current Phase 5 branch: `mdp-v1.2/phase5-gates20-24-parallel`, branched from Phase 4 integration SHA `fcda0ff666eb6c39f90777947d8b70a55a172492`. Phase 5 scope/audit commit `659d51988ce0dd2540a683469907208dd0947894`. **This handoff edit creates a newer HEAD: verify it remotely before claiming same-SHA CI.**
- Phase 4 integration: branch `mdp-v1.2/phase4-gates17-19-parallel`, draft PR **#44** (unmerged). Six technical workflows passed on code SHA `8e44a8584d95dfa6ea5229e9af5072c862fcfb60`; subsequent Phase 4 documentation SHA `fcda0ff6` had mixed completed/in-progress checks at the last audit. PR Checks failed due deferred screenshot requirement. Gates 17–19 remain OPEN; do not claim physical acceptance.
- Earlier draft PRs #40–43 were not merged at Phase 5 startup. Check their current status independently. No physical Golden baselines exist.

## Phase 5 read-only startup audit and next work
- Scope and acceptance directions: `docs/governance/MDP_V1_2_PHASE5_GATES20_24_PARALLEL_SCOPE.md`. Read that file, `PROJECT_LAW.md`, `ACTIVE_CHANGE_GATE.md`, `BASELINES.md`, `CANDIDATES.md` and this handoff before resuming. The older `ACTIVE_CHANGE_GATE.md` contains historical Gate 14/15 text and is not the latest Phase 5 authorization; the user's current approval plus Phase 5 scope govern the new work.
- Gate 20: ball detection/silhouette/observation quality. Existing `src/openflight/camera/ball_silhouette_range.py` estimates a sphere centre from explicit calibrated silhouette rays, known radius and angular residual; `calibrated_rays.py` provides rays. Neither physically detects ball pixels or proves accuracy. Next: audit existing tests and add minimal **pure fail-closed observation-quality validation** with focused tests; no second camera reader.
- Gate 21: clubface detection and 3D pose. Reuse `synthetic_face_landmark_pose.py`, `synthetic_pose_observability.py`, `synthetic_mesh_pose.py`. Reject ambiguous/nonobservable poses and unsupported physical inference.
- Gate 22: contact instant and temporal reconstruction. Inspect single acquisition owner, buffered frame metadata, shot/session identity and timing source. Do not equate host-arrival with exposure timestamp or fabricate subframe contact.
- Gate 23: face-local impact coordinates, centre distance and face boundaries. Reuse `synthetic_observed_impact.py`, `synthetic_impact_pipeline.py`, `synthetic_face_polygon.py` and Phase 4 planar reference contracts; rejected impacts have no coordinates.
- Gate 24: uncertainty, quality controls and explicit rejection. Keep offline residuals separate from physical accuracy and carry provenance into results.
- The canonical Master Development Plan V1.2 file was **not found in the inspected GitHub tree**; Gate names were recovered from prior user-approved conversation. Reconcile before individual closeout; do not invent unverified acceptance criteria.
- The existing `get_synthetic_face_impact` SocketIO endpoint is a synthetic demonstration, **not** a physical ELP measurement publication boundary. Do not gate it on physical calibration or modify unrelated radar processing. Physical mode, lens/crop identity, face pose, real club geometry and physical impact accuracy remain UNKNOWN.
- Candidate registry includes restricted 690CB assets. Do not import restricted models or assume licensing.
- No Phase 5 production code or tests have yet been changed as of this handoff. Phase 5 CI for `659d5198` was not returned by the PR-triggered workflow query (no Phase 5 PR yet); **do not interpret absence of runs as a pass**.

## Resume procedure / evidence discipline
1. Fetch current branch SHA and any PRs from GitHub. Reconcile drift against this snapshot; inspect exact-SHA CI. Do not assume a clean local checkout from remote contents alone.
2. Read Project Law, active scope, baseline/candidate registers, handoff and relevant source/tests. Confirm approved change boundaries before editing.
3. Continue Gate 20 read-only code/test audit, then minimal hardware-free implementation with tests; work Gates 21–24 in parallel only where dependencies allow.
4. Record each new commit SHA, same-SHA CI, changed files, failures and unknowns. Maintain this **top-of-file current handoff** after meaningful milestones and before handing off; keep earlier snapshots below for history.
5. No merges, releases, physical tests, destructive Git operations, screenshot bypass or unsupported physical accuracy claims. Draft PR and exact-SHA CI are separate from Gate acceptance.

---

# GATE 13 USER-APPROVED TECHNICAL CLOSEOUT — 2026-11-10

The user explicitly approved technical closeout of Phase 3 Gate 13 after all technical CI checks passed on exact SHA `b4843c71b326a0c6adb02127d974756bdfec70b7`. This approval **closes Gate 13 technically**, not physically. The previously deferred screenshot-in-PR-description requirement remains **deferred, not waived**, and the PR description completeness check remains failed. Physical ELP camera testing, calibrated measurement validation and end-to-end Electron/Python backend integration remain unverified.

- Branch: `mdp-v1.2/phase3-gate13-camera-preview`; draft PR #39, open/unmerged, stacked on draft PR #38.
- Technical scope delivered: existing USB status and buffered JPEG endpoints integrated into six-panel Camera Preview; honest camera/offline/error and non-measurement states; single camera owner preserved; mocked Playwright coverage.
- All technical checks succeeded on exact pre-closeout SHA `b4843c71b326a0c6adb02127d974756bdfec70b7`: Python 3.10–3.12, Playwright E2E, UI unit, build, lint, formatting, Pylint, Windows diagnostics and quality checks. This governance update creates a new HEAD; recheck exact-SHA CI.
- **No Gate 14 implementation is authorized.** Next permitted work: read-only audit and prepare Gate 14 scope/approval proposal under Project Law V1. No merge, release or physical testing.

---

# CURRENT STATUS OVERRIDE — PHASE 3 GATE 13 TECHNICAL ACCEPTANCE (2026-11-10)

**Read this first.** GitHub is authoritative; verify current branch HEAD, exact-SHA CI, Project Law and PR before continuing. Older handoff sections are archived historical snapshots.

- Repository `andersdui22/openflight-face-impact`; Project Law V1; Master Development Plan V1.2 (8 phases / 35 Gates). No upstream OpenFlight or ConnectorNext modifications.
- Gate 12 was technically closed by user on `fa142ca893a375f9c45a3ef8d962296f92b460dc`. Its draft PR #38 remains unmerged; screenshot requirement deferred, **not waived**.
- Gate 13 explicitly approved by user: integrate existing buffered USB JPEG `/api/camera/preview.jpg` into six-panel Camera Preview, report `/api/camera/usb/status`, preserve single camera reader, show offline/error states, add simulated integration tests. Branch `mdp-v1.2/phase3-gate13-camera-preview`, draft stacked PR #39 https://github.com/andersdui22/openflight-face-impact/pull/39 (unmerged).
- Implementation: `ui/src/components/FaceImpactCameraPreview.tsx` polls backend status every five seconds without overlapping status requests, displays a buffered JPEG still when running, and handles disabled/starting/stopped/error/offline/unavailable JPEG. `ui/src/App.tsx` uses a neutral non-measurement topbar instead of falsely claiming camera offline. No new capture loop.
- Tests: UI SSR component test, four mocked-camera Playwright scenarios, existing dashboard tests and Python camera contract tests. **All technical CI checks passed on exact code SHA `fd49b99167923f066af49877fa18ea4779dea2e5`**: Python 3.10/3.11/3.12, Windows diagnostics, UI unit, E2E, build, lint, Prettier, Pylint and quality checks. PR description completeness remains **failed** because screenshot evidence was deferred; do not bypass or claim pass.
- Limitations: periodic JPEG stills, not a validated continuous live stream; physical ELP camera and calibration have not been tested; no measured impact results. Electron portable EXE remains UI-only without bundled Python backend. Real hardware and backend connectivity are not verified.
- **Gate 13 is technically ready for separate user closeout decision, but remains OPEN.** No Gate 14, merge, release, or physical test authorized. This documentation commit changes HEAD; verify its exact-SHA CI before claiming new HEAD green.

---

# CURRENT STATUS OVERRIDE — PHASE 3 GATE 13 (2026-11-10)

**Read this first.** The Gate 12 and Phase 2 sections below are historical. Verify authoritative GitHub branch HEAD, exact-SHA CI, PR and Project Law before work.

- Repository `andersdui22/openflight-face-impact`; Project Law V1; Master Development Plan V1.2 (8 phases, 35 Gates). Do not change upstream OpenFlight or ConnectorNext.
- **Gate 12 technically closed by user** on `fa142ca893a375f9c45a3ef8d962296f92b460dc`, screenshot evidence deferred, not waived. Draft PR #38 unmerged.
- **User explicitly approved Gate 13** (2026-11-10): wire six-panel Camera Preview to existing `/api/camera/preview.jpg` and `/api/camera/usb/status`, preserve existing single camera owner/buffer, show offline state, add hardware-free integration tests. No Gate 14, physical testing, merges or releases authorized.
- Active branch `mdp-v1.2/phase3-gate13-camera-preview`, stacked on Gate 12; draft PR #39 https://github.com/andersdui22/openflight-face-impact/pull/39 (open/unmerged).
- Implementation: `ui/src/components/FaceImpactCameraPreview.tsx` periodically polls backend status (5 seconds) and requests existing buffered JPEG endpoint when backend reports running; handles disabled, starting, stopped, error, offline and JPEG failure; labels preview as non-measurement. `ui/src/App.tsx` mounts it in Camera Preview. Electron portable UI remains UI-only; Python backend is not bundled. Preview is periodic JPEG stills, not verified live video.
- Tests: `ui/src/components/FaceImpactCameraPreview.test.tsx` contains SSR checking-state test (not part of current UI CI). `ui/tests/e2e/gate13-camera-preview.spec.ts` covers offline backend, stopped camera, backend error and missing JPEG using mocked HTTP responses.
- **Exact verified SHA `db67c925e3a6cd1ded4dfffb70c53b6ca26ce872`: all technical CI succeeded** (UI build, lint, format, Playwright E2E, Python 3.10–3.12, Pylint, quality checks). `PR description completeness` fails due to previously deferred screenshot requirement; do not bypass or claim success. Earlier Prettier failure was corrected and mandatory workflow restored.
- **Known limitations / next Gate 13 tasks:** topbar in `ui/src/App.tsx` still hardcodes “FACE IMPACT CAMERA OFFLINE · SYNTHETIC PREVIEW” even if camera is running; reconcile this without duplicating capture. Check overlapping status polling and recovery behavior. No real ELP hardware test or Golden baseline. Update evidence after changes; each documentation commit changes HEAD and requires rechecking exact-SHA CI. Gate 13 remains open until separate user closeout approval.

---

# CURRENT STATUS OVERRIDE — PHASE 3 GATE 12 (2026-11-10)

**Read this first.** The older Phase 2 text below is historical and no longer the active authorization. GitHub is authoritative; verify HEAD, PR, exact-SHA checks and Project Law before acting.

- Repository `andersdui22/openflight-face-impact`; Project Law V1; Master Development Plan V1.2 (8 phases, 35 gates).
- User approved **Phase 3 Gate 12 only**, explicitly on 2026-11-10: single-owner Windows ELP USB camera architecture, Python/React interface inventory, status/lifecycle contract and hardware-free tests. Gate 13–15 implementation NOT approved. No merges, releases or physical tests.
- Active branch `mdp-v1.2/phase3-gate12-camera-architecture`; base Phase 2 technical-closeout SHA `79549289b7de332a3752f90911850346bcd9fcf0`. Draft PR #38 https://github.com/andersdui22/openflight-face-impact/pull/38 (stacked on Phase 2 draft PR #37). All drafts unmerged.
- Gate 12 architecture document: `docs/governance/MDP_V1_2_PHASE3_GATE12_ARCHITECTURE.md`. Existing `WindowsUsbCamera` has one reader and `TriggeredFrameBuffer`; server already provides `/api/camera/preview.jpg` and `/api/camera/usb/status`; legacy UI `CameraFeed.tsx` is not integrated into six-panel Face Impact dashboard. Phase 2 Electron portable bundle has no Python backend.
- Tests added in `tests/test_windows_usb_camera.py` for idempotent start/single camera owner and release/retry after failed open. Exact test commit `5d6862868d28b026e1c69e56c2cc7d8d7155df22`.
- On exact pre-handoff HEAD `651e54f76f1a5e6ddb78c82a4cb6d4e1bbf49449`, **all technical GitHub CI checks succeeded**, including Windows+Ubuntu USB camera fixtures, Python 3.10–3.12, E2E, UI, lint, format and Windows diagnostics. `PR description completeness` FAILED due to the previously user-deferred screenshot-in-PR-description requirement. Do not waive, bypass or claim it passed.
- This handoff commit changes HEAD: **recheck CI on the new exact SHA** before Gate 12 closeout. No physical evidence or Golden baseline. Gate 12 remains open pending exact-HEAD check and formal closeout; do not begin Gate 13.
- The user previously approved Phase 2 technical closeout on `79549289...` with screenshot still deferred; no merge/release. Prior handoff statements that Gate 10/11 are incomplete are outdated.

---

# CURRENT HANDOFF — OpenFlight Face Impact / MDP V1.2

**Updated:** 2026-11-10. **GitHub is authoritative.** Begin each successor chat with read-only verification of branch HEAD, PR, governance and exact-SHA CI. The archived material below is historical only.

## Active project and governance
- Repository: `andersdui22/openflight-face-impact`. Never modify upstream OpenFlight or ConnectorNext.
- Project Law V1: `docs/governance/PROJECT_LAW.md`. Approved Master Development Plan V1.2: 8 phases, 35 Gates.
- **Current authorization: Phase 2 Gates 09–11 bundled development approved**. User approved completing remaining Phase 2 gates consecutively on 2026-11-10.
- Active branch: `mdp-v1.2/phase2-gate09-demo-mode`, stacked on Gate08 branch `mdp-v1.2/phase2-gate08-ui-contract`. Draft PR **#37**: https://github.com/andersdui22/openflight-face-impact/pull/37. PRs #35 (Gate07) and #36 (Gate08) remain draft/unmerged.
- **Latest known branch commit before this handoff update:** `43842063c4668d0dc7c8b0f3fbee03215cb30531`. Fetch latest HEAD and reverify; handoff update itself changes HEAD.
- `Fortsæt` permits autonomous work within Phase 2 Gates 09–11. No merge, release, physical tests or later phases without separate user approval. Keep PR draft.

## Gate11 packaged EXE smoke verified — 2026-11-10
Exact code SHA `1dbf9d41d553790db4a15c61a1f85ab1aaef6110`: **all technical CI success**, including packaged Windows EXE launch and renderer check of six Face Impact panels. Windows workflow run `42838234719` succeeded. Screenshot artifact `gate11-windows-dashboard-screenshot` ID `13774303142`; portable bundle artifact ID `13774068585`. Screenshot was uploaded but not independently visually reviewed or inserted into PR description. PR description completeness still fails by user-deferred requirement. No physical tests, real ELP measurements, bundled Python backend, merge or release. Gate09–11 closeout evidence now exists; seek explicit Phase 2 closeout approval after rechecking latest HEAD. Latest documentation commit before this handoff update: `696c518c854dd5a74fa36bc6e0d3b441baa9a853`.

## Latest Gate10/11 CI evidence (2026-11-10)
Exact code SHA `9c54404e37bec28e8f7b215f26d276a0a2dc69fa`: **all technical CI passed**, including Windows `portable-exe` job (run `42810519769`), E2E, Prettier, lint, UI build/unit, Python matrix, pylint, Windows diagnostics. Downloadable development-only artifact ID `13761873646` named `gate10-windows-portable-development-only` (161,503,560 bytes) was produced. **Only** PR description completeness fails due to user-deferred screenshot. No GUI startup test, no hardware, no Python backend in portable EXE, no merge/release. Gate11 runtime/visual acceptance remains open. Acceptance evidence recorded in `docs/governance/MDP_V1_2_PHASE2_GATES10_11_ACCEPTANCE.md`. This handoff documentation update changes HEAD; check latest HEAD before declaring same-SHA status.

## Phase 2 bundled authorization — Gates 09–11 (2026-11-10)
User explicitly approved continuing all remaining Phase 2 Gates 09–11 and fixing GitHub CI errors afterward, without per-Gate pauses. This authorization does **not** include merges, releases or physical testing. Governance recorded in `docs/governance/ACTIVE_CHANGE_GATE.md`.
- Gate09 demo CI passed all technical checks on `2bb8e76271ef4bef217edfab9b92f8c110db5e94`. Screenshot-in-PR-description check remains deferred, not waived.
- Gate10 implementation now includes `scripts/build-face-impact-windows.ps1`, relative Vite asset paths, Electron local-file startup for portable mode, and manual-only `.github/workflows/gate10-windows-portable.yml` with bundle artifact validation. This produces a **folder-based EXE**, not a single-file installer, and excludes the Python backend. Windows runtime has **not** been verified.
- Gate11 acceptance checklist in `docs/governance/MDP_V1_2_PHASE2_GATES10_11_ACCEPTANCE.md`; pending new exact-HEAD CI and Windows EXE runtime/visual acceptance.
- Last known commit before this handoff update: `4f121a52b61d32b82d0931212bdd8aa11d7e7673`; fetch authoritative HEAD. PR #37 remains draft and unmerged. Avoid implying packaging is tested or Gate11 is accepted.

## Implemented in active Gate09
- `ui/src/components/FaceImpactSessionDemo.tsx`: deterministic, local React-only simulated shots with mm X/Y sample coordinates; enter/exit, add, reset, shot history, count and averages. Exiting demo clears synthetic session.
- `ui/src/App.tsx`: shared demo state renders points inside existing **Impact Distribution** SVG and a separate clearly labeled **DEMO METRICS — SIMULATED, NOT MEASURED** panel. Actual measurement metrics and legacy OpenFlight shot counts are not overwritten.
- `ui/tests/e2e/gate09-simulated-session.spec.ts`: Playwright lifecycle, plot, averages, reset, exit and clean re-entry.
- Existing six-panel Gate07 dashboard remains; Gate08 UI navigation/reset remain. CAMERA SETTINGS opens legacy OpenFlight Camera view, **not** a working ELP OV9281 Face Impact integration. Real camera and capture controls remain inactive.
- No real measurements, physical testing, hardware camera acquisition, release or merge.

## Verified CI and outstanding work
- On `c15bb140d5ea4e513e05f1e9d3b4e1f8da6d1f82`: E2E, UI build, lint, UI unit, Python tests 3.10/3.11/3.12, pylint and Windows diagnostics passed; Prettier failed on `ui/src/App.tsx`.
- GitHub Actions UI workflow run `42807074528` generated artifact `gate09-prettier-app` (artifact ID `13758513819`) containing exact Prettier-formatted `App.tsx`. On `c102635326f4d614d4b4ccb2aa68fb1323e803f6`, the resulting two formatting differences were applied to `App.tsx`; format and all other technical checks later passed on exact SHA `2bb8e76271ef4bef217edfab9b92f8c110db5e94`.
- Temporary diagnostic steps were **removed** from `.github/workflows/ui-build.yml` in `33e42f7c2003184b4344612c0b2c21e740cf96dd`. The original `npm run format:check` and all other CI checks remain active.
- PR description completeness **fails** due to the previously deferred screenshot-in-description requirement. User explicitly deferred screenshot; never claim waived, bypassed or passed, and do not repeatedly request it.
- **Gate09 closeout proposal:** `docs/governance/MDP_V1_2_PHASE2_GATE09_CLOSEOUT.md` added in `43842063c4668d0dc7c8b0f3fbee03215cb30531`. **Next:** verify exact new HEAD CI including Prettier, E2E, all Python versions, UI unit, build, lint and Windows diagnostics. Ask explicit user approval before closing Gate09 or opening Gate10.
- Minimize unnecessary GitHub Actions runs by batching meaningful changes. Do not disable CI checks without approval.

## Future Gates (NOT authorized)
- Gate10: Windows double-click EXE packaging.
- Gate11: visual and functional acceptance.
- Later phases: real ELP camera acquisition, calibration, geometry, tracking, mathematical impact model, integration and validation.

---

## Archived handoff from previous gate sequence
The material below predates MDP V1.2 and refers to historical Gate 25–31 work. It is retained as archive, **not** the active gate or authorization.

# Active handoff

Current snapshot: 2026-11-09. GitHub is authoritative. Start each session with a read-only audit.

## Gate 31 continuation point — 2026-11-09

- Project Law V1. Anders approved one offline integration from supplied synthetic ball-rim and labelled face pixels to the existing finite-face contact result.
- Branch `gate31/synthetic-observed-impact` starts from Gate 30 `3f91831bd62bd208b131559aa19cac56c41f85f5`. Draft PR #30 recorded seven successful workflows on that exact SHA and remains unmerged.
- [Gate 31 evidence](GATE31_SYNTHETIC_OBSERVED_IMPACT.md) states the input and tolerance contracts. Its draft PR records final same-SHA checks after publication; reverify GitHub before closeout.
- Gate 26 physical testing remains deferred. The current scope does not infer a contact frame or detect real image features. No physical Golden baseline. Next gate requires separate approval.

## Gate 30 continuation point — 2026-11-09

- Project Law V1. Anders approved synthetic planar face pose estimation with labelled correspondences and ambiguity rejection.
- Branch `gate30/synthetic-face-landmark-pose` starts from Gate 29 `9e924d5874f00f51792dddf620624f49a6587d62`. Draft PR #29 recorded seven successful workflows.
- [Gate 30 evidence](GATE30_SYNTHETIC_FACE_POSE.md) describes pose conventions, known metric tests and rejection criteria. [Draft PR #30](https://github.com/andersdui22/openflight-face-impact/pull/30) records the final SHA and CI.
- Gate 26 physical testing remains deferred. Physical landmark detection and end-to-end contact integration remain open. A new gate requires explicit approval.

## Gate 29 continuation point — 2026-11-09

- Project Law V1. Anders approved offline synthetic ball centre estimation from calibrated silhouette rays and an explicit radius.
- Branch `gate29/synthetic-ball-silhouette-range` starts from Gate 28 `60a4232463aed9352cfe7a631394ef6ff26a166f`. Draft PR #28 recorded seven successful workflows.
- [Gate 29 evidence](GATE29_SYNTHETIC_BALL_RANGE.md) describes source reuse, the synthetic range contract and its rejection criteria. [Draft PR #29](https://github.com/andersdui22/openflight-face-impact/pull/29) records the final SHA and CI.
- Gate 26 physical testing remains deferred. Real edge detection, clubface pose and impact remain unverified. A new gate requires explicit approval.

## Gate 28 continuation point — 2026-11-09

- Project Law V1. Anders approved offline ray conversion of synthetic ball and clubface observations.
- Branch `gate28/calibrated-optical-rays` starts from Gate 27 `3fde3dfa53dd8fb40683ebf694abcbb4a5aebc20`. Draft PR #27 recorded seven successful workflows.
- [Gate 28 evidence](GATE28_CALIBRATED_RAYS.md) describes Brown-five correction, synthetic known-ray verification and rejection checks. [Draft PR #28](https://github.com/andersdui22/openflight-face-impact/pull/28) records the final SHA and CI.
- Gate 26 physical testing remains deferred. Depth, world pose and hardware validation remain open. A new gate requires explicit approval.

## Gate 27 continuation point — 2026-11-09

- Project Law V1. Anders explicitly deferred all physical tests and approved offline checkerboard calibration on synthetic images.
- Branch `gate27/offline-checkerboard-calibration` is based on Gate 26 `5ab6f698802fb5d990b0f6a076a0a834e49453c2`. PR #26 remains an open draft with physical evidence pending.
- [Gate 27 scope and evidence](GATE27_OFFLINE_CHECKERBOARD.md) describes the experimental-source adaptation, known-optics checks and held-out image validation. [Draft PR #27](https://github.com/andersdui22/openflight-face-impact/pull/27) records the verified head and CI.
- Hardware calibration and physical Golden remain outstanding. Any next gate requires explicit approval.

## Gate 26 continuation point — 2026-11-09

- Project Law V1. Anders approved the physical ELP operator procedure. Scope and commands are in [Gate 26 ELP operator test](GATE26_ELP_OPERATOR_TEST.md).
- Branch `gate26/elp-operator-test` is based on Gate 25 `4bcb6d311949aa8c3763c957538b419b61f67200`, with eight successful workflows. PR #25 remains an open draft.
- [Draft PR #26](https://github.com/andersdui22/openflight-face-impact/pull/26) records the SHA and CI. Verify them before using the runbook.
- The user-operated Windows ELP test is deferred. No physical evidence or Golden baseline has been collected.

## Gate 25 continuation point — 2026-11-09

- Project Law V1. Anders explicitly approved the Windows desktop smoke and camera test preparation.
- Branch `gate25/windows-desktop-runtime` is based on Gate 24 `e022c2f2348e80d29e4ff3e627669c3dcfa8c645`, with six required successful workflows. PRs #1–#24 were open drafts at startup audit.
- Scope, Windows setup and automated acceptance are in [Gate 25 Windows desktop runtime](GATE25_WINDOWS_DESKTOP_RUNTIME.md). [Draft PR #25](https://github.com/andersdui22/openflight-face-impact/pull/25) records the verified head and CI.
- Physical camera evidence and physical Golden baseline are outstanding. The next physical validation procedure requires separate explicit approval.

## Gate 24 continuation point

- Repository: `andersdui22/openflight-face-impact`. Main: `a3ab081a8abff71fd344d4fd782412d624b99f3f`.
- Project Law V1. Gate 24 implementation is complete. Final closeout is effective after same-SHA CI verification on this documentation commit, recorded on [draft PR #24](https://github.com/andersdui22/openflight-face-impact/pull/24).
- Branch `gate24/react-python-localhost-e2e`, based on Gate 23 `8555d933e781458be5dfae205d1545a9d0369750`. Previously verified implementation HEAD `372aa1707fefba4b158ebeff5c30916f653c5073` passed six required workflows plus Anti-slop Audit. PRs #1–#24 were open, draft and unmerged at audit.
- Gate 24 verifies actual React-to-Python Socket.IO over localhost for synthetic accepted and rejected results, offline error and reconnection. Windows desktop lifecycle and physical measurements remain unverified by these tests. No physical Golden baseline.
- Next: read-only Gate 25 planning for Windows runtime and camera test preparation. Implementation requires separate explicit approval.

The sections below are historical snapshots.

## Authority and state

- User approved Gate 01 with `Det er godkendt. Fortsæt` after the concrete
  foundation-gate request. Project Law V1 is adopted for this project.
- Approved task: repository, governance and CI foundation only.
- Project repository: `andersdui22/openflight-face-impact`, public fork of
  `open-flight/openflight`; remote `main` at the source baseline. Read and
  branch write access are verified for this repository.
- Local preparation branch: `foundation/governance-ci`; remote branch created
  at the source baseline, foundation content not yet published.
- Official source baseline: `open-flight/openflight` `main`
  `a3ab081a8abff71fd344d4fd782412d624b99f3f`.
- Project remote main SHA: `a3ab081a8abff71fd344d4fd782412d624b99f3f`.
  Remote gate branch exists at the same source SHA. Project PRs and CI: **none**.
  Do not invent a same-SHA closeout.
- Completed: Phase 0 audit; Gate 01 local preparation is incomplete.
- Local checks: backend 2,079 passed/7 skipped; isolated geometry 2 passed;
  UI 248 passed plus lint/build/format; strict docs build passed. All are
  Linux results, not project GitHub CI or Windows hardware proof. Details in
  `docs/evidence/GATE01_PREFLIGHT.md`.
- Golden physical baselines: **none**.
- Physical test, merge and release: **not authorized**.

## Technical findings to preserve

The original Python backend and React/Electron UI exist. Pi camera capture,
preview, buffering and replay exist; a Windows ELP USB adapter and camera-only
shot lifecycle do not. Unmerged and forked geometry/Face Impact code exists,
but no validated physical strike-location accuracy. The project manifest
excludes Windows from uv's resolver environment. See
`docs/evidence/PHASE0_AUDIT.md` and `docs/governance/CANDIDATES.md`.

## Current blocker and next authorized action

The browser login was completed by the user, and the fork was created from
the exact official source baseline. The initial GitHub integration write
returned 403 because the new repository was not selected. Anders saved the
installation setting with this repository added while retaining the prior
selection. Branch creation then succeeded. Publish the reviewed foundation
tree, run project CI, open the approved draft PR and close out on its final
same SHA. Do not touch ConnectorNext.

Gate 02 Windows bootstrap is only a future proposal, requiring separate user
authorization after Gate 01 is complete. Recheck source and remote drift
before any resumed work.


## 2026-11-08 remote verification update

A subsequent read-only GitHub verification supersedes the earlier local-preparation
snapshot above. Gate 01 foundation changes were published and draft PR #1 was
opened: https://github.com/andersdui22/openflight-face-impact/pull/1 .
The gate branch and PR head were both verified at
`a6bee2f0cb8eadd88b40c3e80aff5935c0c5ebbf`; main remained at
`a3ab081a8abff71fd344d4fd782412d624b99f3f`.

Seven GitHub Actions workflow runs completed successfully on that exact
pre-document-update SHA: UI, Anti-slop Audit, Face Impact foundation,
PR Checks, Pylint, Documentation, and Tests. These are CI results,
not evidence of physical Windows camera capture or impact accuracy.
The project source and UI were unchanged by PR #1.

IMPORTANT: This handoff update itself changes the branch SHA, so the seven
previous results cannot be used as final same-SHA closeout evidence.
Verify the new remote HEAD and await all required CI checks on the final
documentation SHA before closing Gate 01. No merge, release, physical test,
or Gate 02 production work is authorized by this update.

## 2026-11-08 Gate 03 successor audit — supersedes earlier active-gate instructions

- Authoritative law: `docs/governance/PROJECT_LAW.md` (Project Law V1); active gate: `docs/governance/ACTIVE_CHANGE_GATE.md` and `GATE03_WINDOWS_ELP_CAMERA.md`. Gate 03 was explicitly approved by the user on 2026-11-08.
- Repository: `andersdui22/openflight-face-impact`; working branch `gate03/windows-elp-camera`; base `gate02/windows-bootstrap` at `546eff3f9a761891e16178de40afc617b29960ed`. PR #3 is open, draft, unmerged. PR #1 and #2 are also open draft stacked predecessors.
- Reviewed Gate 03 HEAD before this handoff update: `66d069b759c46a65a67cd0e256516d510304dca5`. This handoff update creates a newer SHA; verify remote HEAD again and never treat checks from an older SHA as final closeout.
- The USB adapter, preview, read-only status API and React status integration exist in the Gate 03 branch. Commit `be9a48ee0310929213e017c239bc2dc772b7d872` normalized JSX conditional formatting. Commit `66d069b759c46a65a67cd0e256516d510304dca5` corrected the USB runbook to reflect the implemented UI status.
- CI: GitHub connector's commit workflow-run and combined-status queries returned empty arrays for the reviewed SHA. This is **unverified**, not evidence of passing or failing. Inspect PR Checks/Actions through an authoritative source before closing Gate 03.
- Real rendered React screenshot is still missing. Do not use generated mockups as evidence. No physical ELP test, hardware FPS proof, Face Impact accuracy, Golden, merge or release has been authorized.
- Next authorized task: reconcile same-SHA CI evidence, investigate any failures, obtain a genuine UI screenshot through a real browser/test environment, and keep PR #3 in draft until acceptance evidence is complete. No ConnectorNext modifications.

## 2026-11-08 Gate 05 current handoff — authoritative successor section

This section supersedes all older "current" instructions above. On every new session verify GitHub HEAD, active gate, draft PRs and same-SHA CI rather than relying on this snapshot.

- Mission: standalone Windows single ELP OV9281 USB-camera Face Impact app, reusing existing OpenFlight backend and React/Electron UI. No ConnectorNext, MLM2PRO, Bluetooth, radar integration or upstream edits.
- Governance: Project Law V1 `docs/governance/PROJECT_LAW.md`. Gate 05 expressly approved by user ("Godkendt", 2026-11-08) after proposal to reuse existing geometry, build synthetic known-dimension calibration and test transforms/unknown inputs. Active gate `docs/governance/ACTIVE_CHANGE_GATE.md`; full scope `docs/governance/GATE05_SYNTHETIC_CALIBRATION.md`.
- Working branch: `gate05/synthetic-camera-calibration`, branched from Gate 04 immutable SHA `0a6aae04901d11b02b90fdc37d80005a731da866`. Gate 04 PR #4 https://github.com/andersdui22/openflight-face-impact/pull/4 is draft, unmerged; all eight workflows succeeded on its exact base SHA. User expressly postponed physical ELP test; do not ask to perform it now or mark it passed.
- Gate 05 initial documentation: `docs/governance/GATE05_CALIBRATION_INVENTORY.md`. Pure `src/openflight/camera/geometry.py::deroll_normalized_offsets` is reusable; existing `tests/test_camera_geometry.py` has two synthetic tests. `club_delivery.py` is experimental and radar-dependent, NOT a Face Impact requirement. `detector.py` ball detector assumes IR-lit dark background; suitability for ELP camera unknown.
- User clarified: club motion metrics (Club Path, AoA, speed, full swing analysis) are NOT product goals. Only short-window clubhead tracking if needed for contact-frame selection; face and ball localization, clubface orientation, contact-time and impact-position estimation are future separately approved gates. Do not develop Face Impact solver in Gate 05.
- Gate 05 approved scope: pure synthetic camera calibration with known reference geometry and millimeter units, explicit coordinate conventions, degenerate/invalid-input rejection, regression tests, documentation and CI. No physical calibration or accuracy claim, no presumed intrinsics, lens distortion, physical camera scale, clubhead mesh truth, or hardware results.
- Current work before this handoff update: Gate 05 branch created; active gate and calibration inventory documents committed. No Gate 05 production calibration code, draft PR or same-SHA CI closeout verified yet. **This handoff commit changes HEAD**; re-fetch HEAD and CI before claiming final checks. Keep all PRs draft and unmerged. Do not merge/release/nominate Golden without separate authorization.
- Next task: inspect existing geometry and test conventions; implement minimal synthetic planar reference mapping in isolated pure code, verify forward/inverse and invalid cases, run CI, open stacked draft PR based on Gate 04 branch, update handoff with verified SHA and CI status. No user physical action required.

## 2026-11-08 Gate 05 CI verification and next-session note

- Draft PR #5: https://github.com/andersdui22/openflight-face-impact/pull/5 ; stacked base Gate 04 `gate04/windows-elp-physical-validation`, unmerged.
- Last verified **pre-handoff** Gate 05 code HEAD: `b5741a00afbeed3619675d83846ac7a52dd1c10a`.
- On that exact SHA, GitHub Actions completed successfully: latest PR Checks run 42526658655 (superseding initial failed PR Checks run 42526592571 caused by nonconforming PR title/body, fixed in PR metadata), Documentation 42526592551, Pylint 42526592604, Tests 42526592599, Face Impact foundation 42526592575, UI 42526592588 (build, format, lint and e2e successful).
- Code: `src/openflight/camera/synthetic_calibration.py` pure affine pixel-to-planar-mm reference mapping and `tests/test_synthetic_calibration.py` hardware-free forward/inverse, degeneracy and invalid-value tests. No integration into live camera or impact computation. Only ideal planar synthetic mathematical behavior verified.
- This documentation commit **changes the branch HEAD**. Recheck exact new SHA and all applicable CI before declaring final same-SHA closeout. Do not conflate previous successful code SHA with a new documentation SHA.
- Keep Gate 05 PR draft and unmerged. Gate 04 physical validation deferred by user. No physical accuracy claim, Golden, merge or release authorization.

## 2026-11-08 Gate 06 active handoff — latest authoritative scope

- Explicit user approval: "Godkendt" to Gate 06 proposal for camera-frame/calibration integration using synthetic test data only, without physical camera testing or Face Impact calculation. Project Law V1 unchanged.
- Working repository `andersdui22/openflight-face-impact`; branch `gate06/synthetic-frame-calibration` created from Gate 05 HEAD `631c7bbb008da94c13a42c8596e4c7a9e589eb80`, which had all six same-SHA CI workflows successful. Gate 05 PR #5 remains draft/unmerged. No merge or release authorization.
- Active gate `docs/governance/ACTIVE_CHANGE_GATE.md`; scope and stop conditions `docs/governance/GATE06_SYNTHETIC_FRAME_INTEGRATION.md`.
- New isolated pure Python adapter `src/openflight/camera/synthetic_frame_calibration.py::map_frame_points_to_millimeters` reuses Gate 05 `SyntheticPlanarCalibration`, checks synthetic frame shape and point bounds, and maps caller-supplied (column,row) points to planar mm. New hardware-free regression tests `tests/test_synthetic_frame_calibration.py`. No automatic point detection, no live capture, no UI changes, no Face Impact solver.
- Gate 04 physical ELP validation remains deferred. No physical calibration/accuracy evidence or Golden baseline.
- At handoff authoring, last code commit `3190972e3d299c9e8e68c7a5df4b4cff2cafa22a`; this handoff commit changes HEAD. Open stacked draft PR #6 targeting Gate 05 branch; check new HEAD and exact-SHA CI before closeout, fix any failures. No physical user action required.

## 2026-11-08 Gate 06 six-workflow CI verification

- Verified draft PR #6 https://github.com/andersdui22/openflight-face-impact/pull/6, unmerged, at exact pre-handoff SHA `3f0653c99ad5f13e281a1fb6264cc158ba0c7fa3`.
- Six GitHub Actions workflows completed successfully on that SHA: Documentation run 42527299416, PR Checks 42527299424, Pylint 42527299573, Face Impact foundation 42527299559, Tests 42527299437, UI 42527299777 (including e2e). No failed workflow reported on that SHA.
- Evidence class: CI/software only. Synthetic frame pixel-coordinate mapping uses caller-supplied points and existing Gate 05 affine transform. No physical camera validation, automatic image detection, impact-location accuracy or Windows clean-install proof.
- This handoff edit creates a **new branch SHA**, so the six successful workflows above are not final same-SHA results for the new HEAD. Recheck and await the applicable CI on the new commit before final closeout.
- Gate 06 remains draft/unmerged; Project Law V1; Gate 04 physical test deferred. No merge/release/Golden authorization.

## 2026-11-08 Gate 07 approved synthetic localization — successor handoff

- Explicit user approval: "Godkendt" to Gate 07 proposal for synthetic ball and clubface localization; no physical ELP camera test or Face Impact computation. Project Law V1 remains unchanged.
- Repository: `andersdui22/openflight-face-impact`; branch `gate07/synthetic-ball-face-localization` based on Gate 06 `9522651a6a4be988f8bd8da22447b50cf1779099`. Gate 06 PR #6 is draft/unmerged; all six CI workflows succeeded on that exact Gate 06 SHA. Earlier PRs #1–#5 remain draft/unmerged. No Golden physical baseline; physical Gate 04 validation deferred.
- Gate: `docs/governance/ACTIVE_CHANGE_GATE.md`; scope `docs/governance/GATE07_SYNTHETIC_LOCALIZATION.md`.
- Source inventory: existing `src/openflight/camera/detector.py::BallDetector` assumes IR-lit ball against dark background and uses OpenCV Hough circles; not verified for ELP or synthetic annotated fixtures. No change to legacy detector, capture, React/Electron UI or calibration. `docs/governance/CANDIDATES.md` retains unadmitted external experiments and restricted mesh concerns.
- New `src/openflight/camera/synthetic_localization.py` recognizes strictly color-coded synthetic RGB fixtures: red perfect disk = ball; green filled rectangle = clubface. It returns pixel centers and bounding boxes, rejects missing/ambiguous/invalid markers. `tests/test_synthetic_localization.py` tests known positions and rejection cases. These synthetic labels do NOT imply automatic recognition of natural images or any physical accuracy.
- Last pre-handoff code commit: `81c6557c1d358053ca0fe36d4d345b28d3d0f0d7`. This documentation commit changes HEAD. Open stacked draft PR #7 targeting Gate 06 branch, then verify GitHub CI on latest exact SHA; diagnose failures without weakening tests. No merge, release or physical user action.

## 2026-11-08 Gate 07 CI and IR illumination evidence update

- User specified a physical 850 nm IR lamp for the planned ELP OV9281 Windows setup. This is user-reported hardware configuration, NOT a completed physical test or proof of detector suitability. No camera test requested or authorized.
- Existing `src/openflight/camera/detector.py::BallDetector` is designed for bright IR-lit ball on dark background and may be a reuse candidate for a later, separately approved real-image gate. No modification to the legacy detector in Gate 07; no assumption that 850 nm alone proves ball/face detection or physical accuracy.
- Verified Gate 07 draft PR #7 https://github.com/andersdui22/openflight-face-impact/pull/7, unmerged, at exact **pre-handoff** SHA `d05547a07a9282957ae67f2e22b13845aa839c23`: all six workflows completed success — PR Checks 42528065219, Documentation 42528065223, Pylint 42528065260, Tests 42528065270, Face Impact foundation 42528065335, UI 42528065222.
- This handoff update creates a NEW branch SHA; verify CI on the resulting SHA before same-SHA closeout. Gate 07 stays draft/unmerged, no physical/accuracy/Golden/merge/release claim.

## 2026-11-08 Gate 08 initial handoff — IR-style synthetic fixtures

- User explicitly approved Gate 08 ("Godkendt") for IR-style ball and clubface localization on synthetic images, reusing existing OpenFlight IR detector. Project Law V1 unchanged; physical tests remain deferred.
- Repository `andersdui22/openflight-face-impact`; branch `gate08/ir-synthetic-detection` from Gate 07 `cb8d13451dac1648d2f5c4f8921a5663ad9eb621` (all six CI successful, draft PR #7 unmerged). Prior PRs #1–#7 draft/unmerged. Golden physical baselines: none.
- Scope: `docs/governance/GATE08_IR_SYNTHETIC_DETECTION.md`; active gate `docs/governance/ACTIVE_CHANGE_GATE.md`.
- Read-only evidence: existing `src/openflight/camera/detector.py::BallDetector` uses OpenCV threshold/blur/HoughCircles and confidence heuristics on IR-bright ball vs dark background; actual ELP OV9281/850 nm image performance unknown. User reported an 850 nm IR lamp, but no physical measurement has been taken.
- Initial change: `tests/test_camera_ir_synthetic.py` exercises the unchanged existing detector with synthetic grayscale disks of controlled brightness and location, including no-detection cases. The fixture is not physical accuracy evidence. Pre-handoff test commit `8a3b4d8d394a88986056d17bce48eff905697dbc`.
- Next: open stacked draft PR #8 against Gate 07; inspect CI on latest handoff SHA, investigate any brittle Hough behavior. Evaluate controlled synthetic face-region detection only with evidence and within approved scope. No live camera, physical test, Face Impact computation, merge or release.

## Gate 08 continuation — synthetic IR face region (2026-11-08)

- Added `src/openflight/camera/synthetic_ir_face.py::locate_synthetic_ir_face` and `tests/test_synthetic_ir_face.py`. The new isolated fixture-only helper accepts exactly one bright filled axis-aligned rectangle in a uint8 grayscale **face-only crop**, returns inclusive pixel bounds and center, and rejects missing, ambiguous, incomplete or malformed synthetic fixtures. This is NOT natural clubface identification or pose estimation; bright reflections are not proof of a clubface.
- Latest **pre-handoff** code SHA `1cd7d87de0b52aa8c64d2ed63fd7658f8735effc`. CI snapshot: Documentation and PR Checks successful; Python Tests, Pylint, Face Impact foundation and UI in progress. Do not claim same-SHA CI success before completion.
- This documentation update advances the branch HEAD again; check the resulting SHA's CI. Keep draft PR #8 stacked on unmerged Gate 07, no physical tests, merge, release or Golden status.

## 2026-11-08 Gate 09 synthetic dual-object pipeline

- User explicitly approved Gate 09 ("Godkendt") for combining existing ball and face synthetic detection in one image process, without physical impact computation or camera testing.
- Branch `gate09/synthetic-dual-object-pipeline` from Gate 08 exact SHA `1bd4ad2919b4817cf3a6a8017f2b4d241684c9ff`, six of six CI success; draft PR #8 unmerged. Project Law V1 unchanged. Active scope in `docs/governance/GATE09_SYNTHETIC_DUAL_PIPELINE.md`.
- Added `src/openflight/camera/synthetic_dual_pipeline.py` composing unchanged `BallDetector.detect` and Gate 08 `locate_synthetic_ir_face` with explicitly supplied face-only crop bounds. Returns both detections in full-frame pixel coordinates, plus frame metadata. Rejects malformed/out-of-bounds crop, missing ball/face, extra bright pixels in crop, and synthetic ball/face overlap. No auto-crop discovery, natural image face recognition, geometry or physical impact inference.
- Added `tests/test_synthetic_dual_pipeline.py` with positive and negative hardware-free fixtures. Last pre-handoff code SHA `69654ddc7f470eb03870d994e4d597d2b92b6484`; CI not yet verified. Create stacked draft PR #9 against Gate 08 and verify all workflows on final SHA.
- No merge, physical tests, release or Golden baseline authorized.

## 2026-11-08 Gate 10 automatic synthetic face candidate proposal

- Explicit user approval "Godkendt" for a hardware-free automatic candidate region proposal on synthetic IR images. Base Gate 09 `c7d881f300b02fc0c6f6f91039e8bbf5f493acf8`, all six latest CI workflows successful; draft PR #9 unmerged. Project Law V1 unchanged.
- Active scope: `docs/governance/GATE10_SYNTHETIC_FACE_PROPOSAL.md`; branch `gate10/synthetic-face-region-proposal`.
- Added `src/openflight/camera/synthetic_face_proposal.py::propose_synthetic_ir_face_region`: connected-components scan of synthetic uint8 grayscale full frame, reuse Gate 08 strict filled-rectangle locator, return exactly one interior rectangular component in full-frame pixel coordinates. Reject zero/multiple rectangles and edge-touching rectangular candidates. Other shapes, such as the round synthetic ball, are not candidates. **This is not real clubface identification.**
- Added `tests/test_synthetic_face_proposal.py` with positive and fail-closed synthetic fixtures. Latest pre-handoff code SHA `420eab7a1ba64c0c6c82c3d2401d4771a65fb5cf`. Same-SHA CI still pending.
- No physical ELP testing, automatic real-world face detection, impact location, merge, release or Golden baseline authorized.


## 2026-11-08 Gate 11 camera-only synthetic 3D projection

User explicitly approved Gate 11 ("Godkendt") after the camera-only 3D projection proposal. Branch `gate11/camera-only-mesh-projection` started from Gate 10 SHA `3b4eca7149dbce637ac66c33a24f14c39bdc01d6`, with six same-SHA successful CI workflows and draft PR #10 unmerged. Scope is synthetic mesh projection with explicit intrinsics and extrinsics, orientation tests and fail-closed invalid calibration. Source references: upstream PR #250 SHA `8d244e25e41764bdeb5665a812af40ccf2e37b16`, `clubpose/mesh.py::rasterize_projected_triangles`, `clubpose/projection.py::_project`; original projection assumes fixed radar/rig world geometry. New isolated helper does not import the restricted 690CB asset. Its cv2 triangle filling is a narrow adaptation of the upstream projected silhouette behavior, not a claim of identical subpixel rasterization. No physical camera, real pose estimation, merge, or release authorized. Await exact-head CI before gate closeout.


## Gate 12 — 2026-11-08

Approved explicitly by user ("Godkendt"). Branch `gate12/synthetic-mesh-pose` starts from Gate 11 SHA `a45bbc93274cac42affe0545b3a06461eb1061a3`, whose six current PR CI workflows succeeded (prior PR title failure corrected). Gate 11 remains draft and unmerged. New synthetic candidate-only silhouette matching reuses Gate 11 camera projection and adapts the IoU fitting idea from upstream open-flight/openflight PR #250 `fit.py` at `8d244e25e41764bdeb5665a812af40ccf2e37b16`. No radar or restricted 690CB mesh. Results are discrete candidates with ambiguity rejection, not real 6DOF, clubface recognition, or millimetre impact measurements. No physical test, merge or release. Same-SHA Gate 12 CI pending.


## Gate 13 — synthetic pose observability (2026-11-08)

User explicitly approved Gate 13. Base Gate 12 SHA `32e09c5190316c082abe0d724acbeda8d9bc55e0` passed six CI workflows. Branch `gate13/synthetic-pose-observability` introduces bounded, candidate-set-specific synthetic silhouette overlap metrics and rejects near-identical orientations as unobservable. Tests include symmetric planar geometry with two distinct rigid orientations yielding identical camera silhouettes. This is NOT a physical angular error estimate, real 6DOF, impact location or a hardware test. Project Law V1, no Golden physical baseline; PR stays draft and unmerged. Exact Gate 13 CI pending.


## Gate 14 — synthetic clubface frame (2026-11-08)

Explicitly approved by user ("Godkendt") after proposal for heel/toe, vertical and center coordinate conventions. Branch `gate14/synthetic-face-coordinate-frame` from Gate 13 SHA `fbbbe9db38dcb4488372493fac1e985b7ae84e66`, six same-SHA successful CI workflows. New `synthetic_face_frame.py` transforms 3D points between world and synthetic clubface coordinates using validated rigid pose and right-handed orthonormal frame; no actual face dimensions, physical center, measurement, camera validation or millimetre impact claim. Tests cover identity, rotation/translation round-trip, signed off-plane distance and fail-closed invalid frames. PR remains draft/unmerged. Gate 14 exact-SHA CI pending.


## Gate 15 — synthetic sphere-plane Face Impact foundation (2026-11-08)

Explicit user approval ("Godkendt") for Gate 15. Branch `gate15/synthetic-ball-face-contact` starts from Gate 14 SHA `eb0ab8e28749758db06274a4214eaec1748bb3df` (six successful CI workflows, draft PR #14 unmerged). Added a strictly synthetic ball-to-infinite-planar-face tangency calculation, signed local mm coordinates and heel/toe/high/low labels. Requires explicitly provided ball radius and known rigid face pose; rejects gaps, penetration, wrong-side contact and invalid geometry. No actual clubhead finite face, curvature, measured ball position, physical impact, camera accuracy or release claim. Same-SHA CI pending. All PRs remain draft and unmerged.


## Gate 16 — finite synthetic clubface bounds (2026-11-09)

User explicitly approved Gate 16 ("Godkendt"). Branch `gate16/synthetic-finite-face-bounds` from Gate 15 SHA `2bb7039112f4089170df916410a565e5900bedff` with six successful same-SHA CI workflows; draft PR #15 unmerged. Adds an explicit positive finite rectangular face width and height (mm), validates Gate 15 tangent point inside inclusive centered edges/corners, rejects outside contact without expanding boundaries by tangency tolerance. Tests cover center, all edges/corners, outside by 0.001 mm, invalid dimensions, rotated face and Gate 15 non-tangency. This is synthetic-only; no real clubhead geometry or camera accuracy. No Golden physical baseline, merge or release. Exact Gate 16 CI pending.


## Gate 17 — synthetic polygonal face footprint (2026-11-09)

Explicit user approval ("Godkendt"). Branch `gate17/synthetic-face-polygon` from Gate 16 SHA `8915eb7f418b1eebf08e2c92a56e87edabee5ba7`, six same-SHA CI successes, draft PR #16 unmerged. Added finite simple polygon boundary in local face millimetres, including asymmetric and concave shapes, inclusive edges and corners, invalid/self-intersecting geometry rejection; reuses Gate 15 tangent calculation and Gate 14 face frame. Synthetic only, no actual clubhead asset, measured impact, physical camera, merge, release or Golden baseline. Same-SHA CI pending.


## Gate 18 — integrated synthetic Face Impact pipeline (2026-11-09)

Explicit user approval ("Godkendt"). Branch `gate18/synthetic-impact-pipeline` from Gate 17 SHA `bb4b6338edbdb1c3135db5d4e01d2b7f38f81dbc`, six same-SHA CI successes; draft PR #17 unmerged. Added `calculate_synthetic_face_impact` composing existing Gate 17 polygon containment and Gate 15 sphere tangency, returning either signed X/Y in mm with heel/toe/high/low labels, or structured outside-face/no-tangency/invalid-geometry rejection without partial coordinates. Synthetic-only known ball/face geometry; no real camera observations, actual pose accuracy, physical impact, merge, release or Golden baseline. Gate 18 exact-SHA CI pending.


## Gate 19 — synthetic Face Impact UI preview (2026-11-09)

Explicit user approval ("Godkendt"). Branch `gate19/synthetic-face-impact-ui` from Gate 18 SHA `fd96259236cc36b69af369e75416731a6dad8444`, six same-SHA CI successes, draft PR #18 unmerged. Added `ui/src/components/FaceImpactView.tsx` with SVG polygon, synthetic marker, signed X/Y millimetres, region labels and rejection state; wired an explicitly synthetic sample into the existing debug panel without replacing original OpenFlight React/Electron UI. Added server-rendered UI component tests. This is not a live backend feed or measured impact; no physical tests, merge, release or Golden baseline. Exact Gate 19 CI pending.


## Gate 20 — synthetic Python-to-React contract (2026-11-09)

User explicitly approved Gate 20 after Gate 19 six-workflow same-SHA success at `70daacd6dc72a9e86f2e952b0d584055ea49b45a`. Branch `gate20/synthetic-impact-contract` stacked on unmerged Gate 19. Gate 20 adds versioned static JSON scenarios `ui/src/data/syntheticFaceImpactCases.json`, Python tests proving the JSON outcomes exactly match `calculate_synthetic_face_impact`, and a React scenario selector inside the original debug panel. The UI displays the backend-shaped results but does not calculate Face Impact or receive a live backend stream. No camera, physical accuracy, merge, release or Golden baseline. Verify Gate 20 remote HEAD and same-SHA CI; this paragraph is a snapshot, not proof of completed checks.


## Gate 21 — local synthetic SocketIO bridge (2026-11-09)

Explicit user approval to reuse the existing Flask-SocketIO Python server and React socket.io-client without live camera or physical tests. Branch `gate21/synthetic-socket-bridge` stacked on Gate 20 exact SHA `ca4e5ebe6ba872ed30383f20bc3fe2c7ef3c6fe2` (six same-SHA successful workflows; PR #20 draft/unmerged). Python `synthetic_impact_socket.py` computes bounded known synthetic cases via Gate 18 pipeline; `server.py` handles `get_synthetic_face_impact` with an acknowledgment payload. The existing frontend socketService requests and validates the versioned response, and the original React diagnostic component shows server results or explicit disconnected/error states. No second socket, real camera observations, physical testing, merge, release or Golden baseline. Gate 21 CI and running-app proof remain pending; verify exact remote SHA before closeout.


## Gate 22 — synthetic Socket.IO integration tests (2026-11-09)

User expressly approved automated integration testing only. Branch `gate22/socket-integration-tests` stacked on Gate 21 `beaa98cb2b634945b696f6bac6f25bfb6c5d01dc` with seven same-SHA workflows successful; PR #21 draft/unmerged. New Python tests exercise Flask-SocketIO's in-process test client, real registered event dispatch and acknowledgment, success/rejection/unknown identifiers and a new session after disconnect. React tests exercise existing socketService with a mocked transport for acknowledgment, invalid/mismatched results, timeout, disconnect and reconnection. Distinguish in-process Python transport and mocked JS transport: this is NOT an end-to-end cross-process live network test, Windows desktop startup proof or camera measurement. No production camera, merge, release or Golden baseline. CI and closeout remain pending.


## Gate 23 — separate-process localhost Socket.IO (2026-11-09)

Explicit approval for synthetic-only localhost network tests. Branch `gate23/localhost-socket-e2e` stacked on Gate 22 `d2435307ac93f6025ac1098e6b5df685226cdf02` (six successful same-SHA workflows, draft PR #22 unmerged). New `tests/test_synthetic_socket_localhost.py` launches the existing Flask-SocketIO app in an isolated child process bound to 127.0.0.1 and exercises actual TCP Socket.IO acknowledgments from a separate python-socketio Client, including accepted and rejected synthetic cases, invalid identifiers, disconnect and a fresh connection. Hardware-oriented server main() is not invoked. This is Python-to-Python network integration, not a real React/Electron runtime, Windows desktop launch or camera measurement. CI verification pending. No merge, release, physical test or Golden baseline.


## Gate 24 — actual React browser-to-Python localhost (2026-11-09)

User expressly approved browser/Socket.IO integration. Branch `gate24/react-python-localhost-e2e` stacked on Gate 23 `8555d933e781458be5dfae205d1545a9d0369750` (six successful same-SHA workflows, PR #23 draft/unmerged). Reuses existing Playwright webServer configuration launching the Python backend in mock mode at 127.0.0.1:8080 and Vite React at 127.0.0.1:5173. New `ui/tests/e2e/synthetic-face-impact-localhost.spec.ts` drives the real debug panel and real browser Socket.IO client for accepted and rejected synthetic Face Impact, offline error and recovery. No browser transport mocks, new production code, camera or physical hardware. See the current continuation point above for CI evidence. Browser test is not Electron packaging or Windows startup proof. No merge, release or Golden baseline.
