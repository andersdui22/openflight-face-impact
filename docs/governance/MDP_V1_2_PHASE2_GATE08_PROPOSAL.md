# Master Development Plan V1.2 — Phase 2, Gate 08: scope proposal and audit

Status: STARTUP AUDIT / SCOPE PROPOSAL ONLY. User approved proceeding after Gate 07 closeout on 2026-11-10; exact Gate 08 deliverables are not yet independently evidenced by an authoritative MDP V1.2 plan document. No implementation is authorized from this proposal alone.

Project Law: V1. Parent Gate 07 governance closeout: `78e81f99930eb2420955a6b846c02e24085ddbbf`.
Branch: `mdp-v1.2/phase2-gate08-ui-contract`. Draft/unmerged only.

## Verified inherited evidence
- Gate 07 complete dark six-panel React UI with local-only settings, disabled camera/calibration/capture/replay actions and synthetic provenance.
- Gate 07 closeout SHA passed build, lint, format, UI unit, Playwright E2E, Python 3.10/3.11/3.12, Pylint and Windows diagnostics.
- PR #35 description screenshot check remains failing because the user explicitly deferred embedding the image. This is not waived.
- Legacy `GATE08_IR_SYNTHETIC_DETECTION.md` is from a different historical gate sequence; it does not authorize current MDP V1.2 Gate 08 implementation.

## Candidate Gate 08 purpose — NOT YET APPROVED AS SCOPE
Define and verify the UI-to-service contract, data provenance and readiness boundaries for a later approved camera integration, without activating physical operations. Proposed activities: read-only inspection of current React/Electron integration and Python `face_impact` package; explicit state model for offline, unavailable, synthetic and validated states; narrowly scoped UI-contract tests. This is a candidate, not a statement of the missing Master Development Plan's actual Gate 08 deliverables.

## Stop conditions
No backend or UI implementation, camera acquisition, algorithms, calibration, persistence, EXE packaging, physical tests, merges, releases or external-repository changes until the actual Gate 08 definition and explicit allowed change scope are reconciled. No synthetic result may be described as measured.

## Next decision
Locate the authoritative Master Development Plan V1.2 Gate 08 specification, or obtain explicit user approval of an amended concrete Gate 08 scope. Then update ACTIVE_CHANGE_GATE and only then implement.
