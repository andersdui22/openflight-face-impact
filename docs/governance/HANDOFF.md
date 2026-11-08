# Active handoff

Snapshot: 2026-11-08 (updated after remote PR/CI verification). GitHub, once created, is authoritative for current
repository state. Start every successor session with a read-only audit.

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
