# CURRENT HANDOFF — OpenFlight Face Impact / MDP V1.2

**Updated:** 2026-11-10. **GitHub is authoritative.** A successor chat must begin with a **read-only startup audit** of branch, HEAD, PR, gate law and CI. This file is maintained on every meaningful change so a new chat can resume without relying on chat history.

## Active project and authority
- Repo: `andersdui22/openflight-face-impact`. Work only in this repo; ConnectorNext and upstream OpenFlight are read-only references.
- Project Law V1: `docs/governance/PROJECT_LAW.md`; approved Master Development Plan V1.2: 8 phases / 35 Gates.
- Current phase/gate: **Phase 2, Gate 08 OPEN** — UI actions, navigation and settings. Gate 07 was separately approved CLOSED.
- Gate 08 branch: `mdp-v1.2/phase2-gate08-ui-contract`; **draft PR #36**: https://github.com/andersdui22/openflight-face-impact/pull/36 ; base branch `mdp-v1.2/phase2-gate07-complete-ui`.
- Approved Gate 07 base SHA: `78e81f99930eb2420955a6b846c02e24085ddbbf`. Gate 08 scope: `docs/governance/MDP_V1_2_PHASE2_GATE08_PROPOSAL.md`; active gate: `docs/governance/ACTIVE_CHANGE_GATE.md`.
- Latest functional/test commit: `13b0db88a685b078d071197bb6b08f0a849c5f15` (navigation/disabled-action E2E extension). Latest governance commit before this handoff: `95581e2b8bf28fa0242a87cd7e87056fd720b07b`. **Reverify branch HEAD and CI after this handoff commit**.

## Implemented
- Gate 07 six-panel dark dashboard: Side Impact, Front Impact, Top Impact, Impact Distribution, Camera Preview, Shot Replay.
- Gate 07 four control tabs: Camera setup, Calibration, Capture, Replay. Handedness, camera position, overlay are local-only; future physical actions are explicitly disabled.
- Gate 08: `RESET LOCAL SETTINGS` restores right-handed / face-on / overlay enabled. Playwright tests verify reset, tab navigation, and that capture/replay remain disabled.
- Modified Gate 08 files: `ui/src/components/FaceImpactControls.tsx`, `ui/tests/e2e/gate07-controls-interaction.spec.ts`, Gate 08 governance docs, active gate and this handoff.

## CI evidence and pending checks
- PR #36 at SHA `d17891da7c65242f094faa664dafc2607ccade4c`: build, lint, format, UI unit, E2E, Python 3.10/3.11/3.12, pylint, Windows diagnostics **passed**. PR description completeness **failed** due to screenshot embedded-description requirement.
- Latest E2E extension at `13b0db88...` and subsequent governance commits are **not yet recorded as same-SHA green**. Verify current SHA check-runs before claiming success.
- User explicitly deferred inserting the dashboard image; do not ask repeatedly, waive, or bypass screenshot requirement. Playwright screenshot artifact exists from Gate 07. PR #35 remains draft/unmerged; its description check also fails.
- No merges, releases or physical tests have been authorized.

## Next autonomous actions within Gate 08
1. Read-only GitHub audit of current branch SHA, PR #36 checks, changed files, and Project Law V1.
2. If CI fails for code/test reasons, repair only Gate 08 UI/test scope and rerun CI.
3. Audit all enabled Face Impact UI controls for meaningful behavior; add narrow UI-only wiring and tests, keeping unavailable physical features disabled and provenance honest.
4. Keep this handoff current after each meaningful commit; record exact latest HEAD and test evidence. Do not declare Gate 08 closed without explicit user approval.

## Future gates (NOT authorized)
- Gate 09: simulated shots/demo, impact points, sessions and statistics.
- Gate 10: double-click Windows EXE.
- Gate 11: visual/functional acceptance.
- No camera acquisition, calibration measurement algorithms, real impact claims, merges, releases or physical testing in Gate 08.

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
