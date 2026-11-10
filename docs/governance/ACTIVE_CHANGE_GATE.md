# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE

Current plan: Master Development Plan V1.2
Current gate: Phase 2 / Gate 05 — standalone Face Impact project isolation
Status: APPROVED for bounded implementation, 2026-11-10 (user authorization in conversation).
Project Law: V1
Approved base: `d78fb3cbef96e10e75eb9b03c0a0370257cea3ae`
Working branch: `mdp-v1.2/phase2-gate05-isolation`
Gate detail: [MDP_V1_2_PHASE2_GATE05.md](MDP_V1_2_PHASE2_GATE05.md)

Authorized: governance alignment, additive `src/face_impact/` package skeleton and focused import-isolation tests.
Excluded: changes to `src/openflight/`, `ui/`, dependency manifests, build scripts, measurement algorithms, hardware tests, merges, releases, other repositories, and all ConnectorNext work.
Acceptance: no import-time dependency on OpenFlight/radar/camera hardware, relevant tests and same-SHA verification; no behavior regression.
Stop: unapproved scope expansion, unknown license/dependency, conflicting remote changes or insufficient evidence.

## Legacy gate preservation
The former Gate 32 dashboard authorization and stacked draft PR #32 remain historical evidence, not authority for this new Gate 05. Original legacy gate text at the approved base commit:
https://github.com/andersdui22/openflight-face-impact/blob/d78fb3cbef96e10e75eb9b03c0a0370257cea3ae/docs/governance/ACTIVE_CHANGE_GATE.md
