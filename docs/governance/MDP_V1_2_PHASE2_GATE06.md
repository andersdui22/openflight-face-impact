# Master Development Plan V1.2 — Phase 2, Gate 06

Status: ACTIVE. Explicitly opened by the user on 2026-11-10 after approving Gate 05 closeout.
Project Law: V1. Gate 05 baseline: `f9afc6f6b66ec9630d593b184cbdb33a4ed7f020`.
Branch: `mdp-v1.2/phase2-gate06-dashboard`.
Gate 05 remains a draft PR #33, unmerged. Gate 06 changes must stay stacked and draft.

## Mission
Preserve and complete the existing dark React/Electron Face Impact dashboard, including its six panels, without replacing its layout or introducing unapproved measurement capabilities.

## Required six-panel dashboard contract
1. Side Impact — synthetic Face Impact demo remains explicitly synthetic.
2. Front Impact — placeholder, not a real camera measurement.
3. Top Impact — placeholder, not a real camera measurement.
4. Impact Distribution — no invented historical measurements.
5. Camera Preview — clearly unavailable until approved camera integration.
6. Shot Replay — clearly unavailable until real shot capture/replay exists.

Keep the dark visual hierarchy, panel styling, metrics, and current responsive structure. Preserve provenance and reject any misleading physical-accuracy claim.

## Approved implementation scope
- Dashboard React/CSS only where necessary to preserve existing appearance and fix demonstrable issues.
- Prettier-only normalization of `ui/src/App.tsx` and `ui/src/components/panel/panel.css`, identified by Gate 05 CI as pre-existing format failures.
- Narrow automated dashboard-preservation tests and relevant governance documents.
- No camera capture, geometry, marker tracking, shot recording, backend integration changes, navigation expansion (Gate 07), or packaging (Gate 09).

## Evidence and acceptance
- Verify exact six titles and their existing demo/placeholder semantics on the approved baseline.
- Verify no misleading measured values are introduced.
- Run React build, lint, unit and E2E tests; check Prettier against `ui/src/`.
- Compare changed files against the Gate 05 SHA and ensure no out-of-scope modifications.
- Record test and CI results at a single immutable head SHA; explicitly classify baseline failures.
- Request separate user approval to close Gate 06 and open Gate 07. Never merge or release.

## Current findings
The inherited Gate 05 CI format job fails in `ui/src/App.tsx` and `ui/src/components/panel/panel.css`. The other Gate 05 workflows passed. These two files were not changed in Gate 05. They remain unresolved until actual Prettier output can be verified; do not claim formatting is fixed by inspection.
