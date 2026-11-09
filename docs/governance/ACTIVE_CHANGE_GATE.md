# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 19

Title: Synthetic Face Impact visualization in existing OpenFlight React UI
State: ACTIVE — user explicitly approved "Godkendt" (2026-11-09).
Project Law: V1 unchanged.
Working branch: `gate19/synthetic-face-impact-ui`.
Base: Gate 18 `fd96259236cc36b69af369e75416731a6dad8444`, six successful same-SHA CI workflows; draft PR #18 unmerged.

## Authorized scope
Create an accessible, self-contained React Face Impact visual component using explicit synthetic polygon vertices and Gate 18 result-shaped fixture data. Render face outline, impact point, X/Y in millimetres, heel/toe and high/low, and clear rejection messages without plotting a rejected impact. Add component to the existing OpenFlight UI in a visibly synthetic-only diagnostic context, retaining the original React/Electron shell and navigation. Include deterministic component tests.

## Acceptance
Synthetic fixture clearly labelled and not presented as a real camera measurement. Preserve existing UI and workflows. Same-SHA CI required.

## Exclusions
No backend API/wire protocol, live camera observations, physical accuracy, real clubface mesh, production impact stream, radar, merge, release or Golden baseline.
