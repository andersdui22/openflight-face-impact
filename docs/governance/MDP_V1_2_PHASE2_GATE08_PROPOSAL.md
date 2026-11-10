# Master Development Plan V1.2 — Phase 2, Gate 08: UI actions, navigation and settings

Status: OPEN for scoped Gate 08 planning and implementation after user's separate "Godkendt" following Gate 07 closeout (2026-11-10). Implementation must follow Project Law V1 and the read-only source audit. This document corrects the superseded UI-to-service-contract proposal.

Project Law: V1. Base Gate 07 closeout: `78e81f99930eb2420955a6b846c02e24085ddbbf`.
Branch: `mdp-v1.2/phase2-gate08-ui-contract`. No merges/releases/physical tests.

## Authoritative original Master Development Plan V1.2 sequence
- Phase 2 Gate 08: implement all UI actions, navigation and settings. No dead buttons: each action has a defined outcome.
- Phase 2 Gate 09: demo mode with simulated shots, impact points, sessions and statistics.
- Phase 2 Gate 10: Windows/Electron/Python EXE.
- Phase 2 Gate 11: visual and functional acceptance test.

This sequence was recovered from the original user-approved planning conversation. The previous candidate "UI-to-service contract" was not the approved Gate 08 purpose and is withdrawn. The historical `GATE08_IR_SYNTHETIC_DETECTION.md` belongs to another gate sequence.

## Gate 08 implementation boundary
Allowed: existing React UI action wiring, navigation, local settings state, honest disabled/unavailable actions with visible explanation, keyboard/accessibility, and focused tests. Existing OpenFlight behavior must be preserved.
- Every visible enabled button, tab, link and selector must have a meaningful deterministic UI-only result.
- Unavailable physical actions must remain disabled or explain their unavailability; do not pretend a camera, calibration, capture or replay works.
- Settings may be local-only, explicitly labeled as not persisted; no invented backend persistence.
- Preserve the six-panel dashboard and synthetic/measurement provenance.
- Do not preempt Gate 09 demo mode, Gate 10 EXE packaging, or any real hardware/measurement phase.

## Audit and acceptance
1. Inspect actual existing UI controls and routes, list no-op/ambiguous actions before editing.
2. Make the smallest justified in-scope changes with regression tests.
3. Verify build, lint, format, UI unit, Playwright E2E and other applicable CI on same SHA.
4. Record unresolved controls that depend on future Gates rather than falsely activating them.
5. Gate 08 closeout requires separate user approval.

## Known inherited exception
PR #35 screenshot description completeness check remains failing because user deferred embedding the screenshot. It is not waived. Gate 07 technical CI passed at `78e81f99930eb2420955a6b846c02e24085ddbbf`. Draft PRs remain unmerged.
