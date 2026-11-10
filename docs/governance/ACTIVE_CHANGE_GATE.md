# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE

Current plan: Master Development Plan V1.2
Current gate: Phase 2 / Gate 09 — simulated demo mode
Status: Gate 08 CLOSED on approved commit `5c71d6a5c599a7fde17bbfc34bbc834160666e70`; Gate 09 OPEN by explicit user approval on 2026-11-10.
Project Law: V1
Approved Gate 09 base: `5c71d6a5c599a7fde17bbfc34bbc834160666e70` (Gate 08 user-approved closeout)
Working branch: `mdp-v1.2/phase2-gate09-demo-mode`
Gate detail: [MDP_V1_2_PHASE2_GATE08_PROPOSAL.md](MDP_V1_2_PHASE2_GATE08_PROPOSAL.md)

Authorized: explicitly simulated demo shots, local sessions, impact points and statistics, scoped UI tests and governance documentation.
Excluded: real camera acquisition, real measurements, calibration algorithms, hardware testing, EXE packaging (Gate 10), changes to other repositories, merges and releases.
Acceptance: demonstrable simulated shots, impact points, session history and statistics, clearly separated from actual measurements, preserving the six-panel dashboard; verify CI before closeout.
Stop: changes outside scope, invented measurements, misleading active controls, unapproved merges/releases/physical tests.

## Gate history
Gate 05 approved closed with inherited Prettier issue transferred to Gate 06. Gate 06 approved closed on `681531697366d14a1089ea11dc13d54348f78311`, after pinned Prettier fix and passing latest CI checks. Historical draft PRs #33 and #34 remain unmerged. Gate 07 is user-approved closed after passing technical CI at `7ed0d10167c3081a4f428d190054b0c207918784`; draft PR #35 remains unmerged. The PR screenshot check remains failing by documented user-deferred exception; it was not waived. Gate 08 is OPEN, separately approved after Gate 07 closeout.

## Change freeze after Gate 07 closeout
No further implementation under Gate 07. Gate 08 permits only its documented UI-only scope. No Gate 09+, merge, release, camera integration, physical testing or EXE packaging without separate explicit authorization.

## Gate 08 authority and bounded implementation
Original MDP V1.2 Phase 2 Gate 08: implement UI actions, navigation and settings; no dead buttons. Base Gate 07 closeout SHA: `78e81f99930eb2420955a6b846c02e24085ddbbf`. Allowed: existing React UI-only wiring, navigation, local settings and focused tests. Excluded: Gate 09 synthetic demo mode, Gate 10 EXE, camera, real calibration/capture/replay, backend, physical tests, merges, releases. Unavailable actions must be clearly disabled or explained. Closeout requires separate approval.

## Gate 09 implementation
Gate 08 was explicitly closed and Gate 09 opened by user approval. First demo-session component is local-only and deterministic; further visualization, tests and CI are pending. Screenshot PR requirement remains deferred, not waived. No merges, releases or physical tests.
