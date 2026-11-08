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
