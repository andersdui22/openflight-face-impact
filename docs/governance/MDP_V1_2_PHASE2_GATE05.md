# MDP V1.2 — Phase 2, Gate 05: Face Impact isolation

Status: ACTIVE — user approved 2026-11-10 in conversation.
Project Law: V1. Gate 04 and System Architecture Specification V1.0 approved.
Approved base commit: `d78fb3cbef96e10e75eb9b03c0a0370257cea3ae`.
Working branch: `mdp-v1.2/phase2-gate05-isolation`.
Legacy Gate 32 remains an unmerged draft PR #32; it is NOT this Gate 05.

## Mission
Introduce a minimal, independent Python namespace for the standalone Windows Face Impact application, without copying, changing or importing legacy radar, BLE, simulator or Raspberry Pi runtime code. Preserve the existing React/Electron dashboard and OpenFlight provenance.

## Authorized changes
- Governance documentation needed to record this approved gate and architecture boundary.
- Additive `src/face_impact/` Python package skeleton and narrow import-boundary tests only.
- No changes to legacy `src/openflight/` code, `ui/` dashboard, dependency manifests, build scripts, camera algorithms, physical measurement code, or packaging.

## Architecture boundary
- `face_impact` is a standalone package namespace; its root import must have no side effects and must not import `openflight`.
- Future camera ownership, engine, service and storage responsibilities will be introduced only in separately approved Gates.
- Existing OpenFlight modules are read-only references for selective, licensed reuse in later Gates. Do not import `openflight.camera` transitively from the new root.
- A single camera acquisition owner and honest timestamp semantics remain mandatory.
- React/Electron remains the only UI; this gate does not duplicate or rewrite it.

## Acceptance
1. New branch based exactly on the approved base SHA; no change to main or the stacked draft PRs.
2. A minimal Python package can be imported without importing `openflight`, `cv2`, radar or hardware drivers.
3. Narrow automated test asserts the isolation contract.
4. No behavior change to existing OpenFlight source, UI or tests.
5. Verify the final branch SHA and relevant CI before requesting Gate 05 closeout.

## Stop conditions
Any need for changing legacy runtime, adding dependencies, changing UI, merging, releasing, physical testing, or copying restricted assets requires separate approval. CI failures must be reported honestly. Gate 05 does not authorize opening Gate 06.

## Evidence
GitHub source baseline: `gate32/face-impact-dashboard` at `d78fb3cbef96e10e75eb9b03c0a0370257cea3ae`.
Existing baseline has passing and failing workflows; no physical Golden baseline. Full Windows packaging and camera measurements remain unverified.
