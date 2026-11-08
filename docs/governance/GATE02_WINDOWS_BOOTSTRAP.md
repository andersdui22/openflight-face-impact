# ACTIVE CHANGE GATE 02 — Windows Bootstrap

State: ACTIVE (approved by user on 2026-11-08, after Gate 01)
Project Law: V1, unchanged.
Repository: andersdui22/openflight-face-impact
Working branch: gate02/windows-bootstrap
Base: foundation/governance-ci @ bf2111aadc834373b5a072197d6c82b40b675d6c
Gate 01: all seven workflows success on exact bf2111aa; draft PR #1 remains unmerged.
Approval: user expressly approved the scoped Windows Bootstrap gate, and subsequently instructed autonomous continuation.

## Objective
Start the existing Python Flask backend in hardware-free mock mode on Windows,
wait for HTTP readiness, then open the existing React/Electron UI. Provide
bounded failure handling and coordinated shutdown without changing any camera,
radar, BLE, or Face Impact behavior.

## Allowed
A minimal Windows-specific launcher, focused unit/integration tests, necessary
Windows dependency-resolution adjustments if evidence-backed, CI verification,
documentation, and a draft Gate 02 PR. Reuse upstream backend, UI and Electron
entry points. No duplicate UI or backend.

## Excluded
ConnectorNext, MLM2PRO, hardware capture, physical tests, geometry/pose solver,
new camera adapter, release/publish, merge, Golden designation, and unrelated
refactoring or dependency upgrades.

## Acceptance
1. Launcher checks prerequisites and starts backend in --mock mode bound to
127.0.0.1, waits for HTTP readiness, then launches existing Electron UI.
2. Startup timeout, premature exit, and shutdown are handled without orphaning
the child processes under supported conditions.
3. Windows CI validates launcher behavior with controlled process fixtures;
a real backend smoke test is added only if dependencies resolve honestly.
4. UI remains upstream-identical; exact tested SHA and unresolved Windows
hardware/package gaps are recorded.
5. Draft PR remains unmerged and no release is produced.

## Stop conditions
Unapproved scope expansion, incompatible dependencies, unresolved source
licensing, destructive Git operation, physical hardware testing, or missing
required verification. Do not silently weaken checks.

## Current
Gate 02 branch created from verified Gate 01 head. No physical Golden exists.
