# OPENFLIGHT FACE IMPACT - ACTIVE CHANGE GATE 01

Title: Repository, governance and CI foundation
State: ACTIVE; FOUNDATION DIFF AND CI PENDING, NOT CLOSED
Law: Project Law V1 adopted with this gate
Authorization: Anders Nørgaard, `Det er godkendt. Fortsæt` (2026-11-08),
in response to the explicit Gate 01 approval request.
Destination: `andersdui22/openflight-face-impact`, public fork of official
OpenFlight, created 2026-11-08 under the only connected owner. Its main HEAD
is the verified source baseline.
Working branch: `foundation/governance-ci` (created remotely at source SHA)
Project remote `main` HEAD: `a3ab081a8abff71fd344d4fd782412d624b99f3f`
Project remote gate branch: created at source baseline; foundation commit pending
Source baseline: `open-flight/openflight@a3ab081a8abff71fd344d4fd782412d624b99f3f`

## Purpose

Establish an authoritative, reviewable project and verification foundation while preserving OpenFlight's existing software unchanged. This gate does not implement the Windows app or validate camera-only impact measurement.

## Approved scope

The user approved adoption of Project Law V1, creation of the new repository,
non-destructive baseline seeding from the re-audited official source, and a
foundation branch containing governance/documentation plus CI-only changes.
Public visibility was the proposal for public upstream code and project
documents. Creation capability and branch access must be established before an
external write. No secrets, personal capture data or restricted mesh assets may
be uploaded.

No merge or release authorization is included. The initial reference seeding is explicitly part of this proposal and must not be treated as a general merge exception.

## Mandatory preflight

1. Read the approved law, gate and audit; record the user's approval evidence.
2. Reverify official default branch, remote HEAD, PR #245/#250 and known candidate heads. If upstream has moved, audit the delta before adopting a different baseline.
3. Confirm exact new owner/name, visibility and create/write access. Check that the target does not already contain work; never overwrite an existing repository.
4. Inspect existing CI, GitHub governance, workflows and upstream license. Search for equivalent project documents before adding them.
5. Verify existing source hashes and prepare the smallest allowed diff.

## Allowed changes

| Location / action | Allowed purpose |
| --- | --- |
| New repository and initial refs | Preserve upstream history and seed the verified source baseline without rewriting upstream. |
| `AGENTS.md` | Minimal project-specific entry guidance and pointers to the law/gate; keep relevant upstream attribution. |
| `docs/governance/PROJECT_LAW.md` | Adopt V1 as approved. |
| `docs/governance/ACTIVE_CHANGE_GATE.md` | Record Gate 01 authorization, SHA scope and acceptance evidence. |
| `docs/governance/BASELINES.md` | Source baseline plus an explicitly empty physical-Golden register. |
| `docs/governance/CANDIDATES.md` | Pinned experimental candidates, dependencies, duplicates, provenance and no implicit admission. |
| `docs/governance/HANDOFF.md` and evidence/decision/test records | Knowledge rebuild and same-SHA closeout. |
| `UPSTREAM.md`, `THIRD_PARTY_NOTICES.md` | Attribution, license position and restricted assets; do not replace upstream LICENSE. |
| `.github/workflows/face-impact-foundation.yml` | Scoped verification with Linux and Windows jobs; no release or publish action. |
| New foundation-only CI support, if strictly necessary | Documented narrow scripts that inspect policy/source and run existing checks; no app behavior. |

All existing application source, UI behavior, models, package/dependency manifests and lockfiles remain byte-identical to the source baseline. Existing unrelated upstream workflows must be reviewed before enabling; do not enable deploy/cloud/publish jobs by accident. Any necessary workflow-enablement change must be explained as CI configuration, not product development.

## Explicit exclusions

No camera adapter, production bootstrap, solver/pose changes, experimental code import, calibration, new UI, branding redesign, dependency upgrades, radar/Bluetooth work, ConnectorNext access, hardware test, branch deletion, history rewrite, merge, release or release-candidate publication.

No empty placeholder production modules. A file path in the proposed repository structure is not permission to create it.

## Acceptance criteria

1. The new remote repository exists at the agreed destination. Its initial source commit and provenance match the reverified upstream baseline, with history and AGPL preserved.
2. The approved law, active gate, baseline/candidate/evidence registers and next-session startup procedure are present and internally consistent.
3. A diff against the source baseline shows only the allowed governance, documentation and CI changes. Application source, assets, manifests and lockfiles are unchanged.
4. Linux CI runs the existing applicable backend tests and UI lint/test/build. Findings are classified; failures are not hidden or fixed by expanding this gate. Baseline failures blocking acceptance require a scoped amendment or later gate.
5. Windows CI builds the existing React UI and records Python/Node/dependency environment diagnostics. Reuse a focused existing pure backend test subset when the environment supports it. Document exactly what ran. Do not claim Electron/backend startup, USB acquisition or packaging from these checks. The main resolver's declared Windows exclusion is a recorded product gap, not a reason to alter the manifest under this gate.
6. CI has no release/deploy steps and runs are bounded by relevant paths or explicit dispatch. Obtain one complete required result set on the final gate SHA; unnecessary repeated runs are avoided.
7. A draft PR contains the concrete foundation diff and honest validation. Opening this project PR is included in Gate 01 if the approved destination and permissions allow it; no comments to third parties are authorized.
8. Closeout re-fetches the gate branch, PR head and checks. The recorded final SHA is the same one reviewed and tested. Remaining unknowns and the next proposed gate are documented.
9. Physical-Golden register remains empty. No merge or release occurs.

## Test/evidence plan

Record baseline HEAD and required checks before changes. Run focused governance/source-integrity checks, existing relevant backend regression on Linux, UI lint/test/build and Windows UI build. Capture exact commands, tool versions, SHA, pass/fail/skip counts and CI URLs. A missing dependency is environmental until investigated; do not classify it as product correctness or silently substitute a mock.

Source integrity, not a new behavior test suite, verifies that this foundation gate preserved production files. Windows compatibility remains partial until the later bootstrap/camera gates pass their own tests.

## Stops and blockers

Stop the affected action for missing approval, absent create/write access, ambiguous owner, existing target work, remote drift not reconciled, required source-integrity failure, unrelated workflows with unsafe publication side effects, or any requested production change. Continue independent authorized documentation and read-only analysis. Never use access to ConnectorNext as a substitute destination.

Phase 0 attempted no repository creation. Gate 01 created the fork and verified
its source SHA. Anders added this specific repository to the existing GitHub
integration; branch creation then succeeded at the source baseline. Publishing
the foundation diff, project CI and draft PR remain pending.

## Closeout fields to fill during execution

Approval evidence: User's 2026-11-08 `Det er godkendt. Fortsæt`, following the Gate 01 request.
Actual owner/name and visibility: `andersdui22/openflight-face-impact`, public fork created.
Baseline remote SHA: `a3ab081a8abff71fd344d4fd782412d624b99f3f`, matched official main and local full-history partial clone.
Final gate remote SHA: PENDING - remote branch currently at source baseline
Draft PR: NONE
Required check results: NOT RUN on project remote; local Linux checks recorded in `docs/evidence/GATE01_PREFLIGHT.md`.
Physical testing: NOT AUTHORIZED
Merge/release: NOT AUTHORIZED
Next task after closeout: propose Gate 02 for minimal Windows bootstrap and dependency admission; requires separate authorization.
