# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 20

Title: Synthetic Python-to-React Face Impact result contract and selectable fixtures
State: ACTIVE — user explicitly approved Gate 20 (2026-11-09).
Project Law: V1 unchanged.
Working branch: `gate20/synthetic-impact-contract`.
Base: Gate 19 `70daacd6dc72a9e86f2e952b0d584055ea49b45a`, six same-SHA successful workflows; draft PR #19 unmerged.

## Authorized scope
Define a deterministic JSON-shaped shared synthetic Face Impact result contract using the existing Gate 18 Python pipeline output. Verify fixture parity against actual Python calculation and consume the same fixtures in the original React/Electron diagnostic panel, with selectable success/rejection scenarios. Preserve the existing renderer and original UI. Tests must ensure the renderer does not fabricate contact coordinates for rejected results.

## Acceptance
Python fixture parity, React scenario tests, no new measurement solver in UI, six successful workflows on identical Gate 20 SHA.

## Exclusions
No runtime backend API or live camera connection, real measurements, physical tests, ConnectorNext, MLM2PRO, radar, merge, release or Golden baseline.
