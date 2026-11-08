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
