# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE

Current plan: Master Development Plan V1.2
Current gate: Phase 2 / Gate 08 — UI actions, navigation and settings
Status: Gate 08 OPEN after separate user approval ("Godkendt"), 2026-11-10. Gate 07 closed.
Project Law: V1
Approved base: `681531697366d14a1089ea11dc13d54348f78311` (Gate 06 user-approved closeout)
Working branch: `mdp-v1.2/phase2-gate08-ui-contract`
Gate detail: [MDP_V1_2_PHASE2_GATE08_PROPOSAL.md](MDP_V1_2_PHASE2_GATE08_PROPOSAL.md)

Authorized: visible Face Impact dashboard UI, navigation, fields, buttons, settings controls, clearly disabled future functions, scoped UI tests, and governance documentation.
Excluded: backend, actual camera acquisition, measurements, calibration algorithms, hardware testing, EXE packaging (Gate 09), changes to other repositories, merges and releases.
Acceptance: all six original panels preserved; complete planned visual UI and discoverable controls; honest unavailable/synthetic state; keyboard accessibility; UI build, lint, formatting, unit and E2E checks verified.
Stop: changes outside scope, invented measurements, misleading active controls, unapproved merges/releases/physical tests.

## Gate history
Gate 05 approved closed with inherited Prettier issue transferred to Gate 06. Gate 06 approved closed on `681531697366d14a1089ea11dc13d54348f78311`, after pinned Prettier fix and passing latest CI checks. Historical draft PRs #33 and #34 remain unmerged. Gate 07 is user-approved closed after passing technical CI at `7ed0d10167c3081a4f428d190054b0c207918784`; draft PR #35 remains unmerged. The PR screenshot check remains failing by documented user-deferred exception; it was not waived. Gate 08 is NOT open.

## Change freeze after Gate 07 closeout
No further implementation under Gate 07. Governance-only closeout commits require CI verification. No new Gate, merge, release, camera integration, physical testing or EXE packaging without separate explicit authorization.

## Gate 08 authority and bounded implementation
Original MDP V1.2 Phase 2 Gate 08: implement UI actions, navigation and settings; no dead buttons. Base Gate 07 closeout SHA: `78e81f99930eb2420955a6b846c02e24085ddbbf`. Allowed: existing React UI-only wiring, navigation, local settings and focused tests. Excluded: Gate 09 synthetic demo mode, Gate 10 EXE, camera, real calibration/capture/replay, backend, physical tests, merges, releases. Unavailable actions must be clearly disabled or explained. Closeout requires separate approval.
