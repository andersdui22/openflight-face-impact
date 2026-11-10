# Master Development Plan V1.2 — Phase 2, Gate 07

Status: ACTIVE, explicitly approved by the user on 2026-11-10.
Project Law: V1. Gate 06 closeout SHA: `681531697366d14a1089ea11dc13d54348f78311`.
Branch: `mdp-v1.2/phase2-gate07-complete-ui`. Draft stacked PR only; no merges/releases.

## Mission
Complete the visible Face Impact UI so the user can explore every planned dashboard section, field, control and settings affordance before camera integration. Retain the existing dark six-panel layout and responsive structure.

## Visual contract
- Side Impact: explicitly synthetic preview, clearly separated from measured output.
- Front Impact and Top Impact: placeholders with visual geometry guides; never imply measured positions.
- Impact Distribution: empty history visualization until real validated shots.
- Camera Preview: ELP OV9281 identity, offline/no-feed state and visible setup controls.
- Shot Replay: empty state with visible future playback controls, disabled until a captured shot exists.
- Metrics: heel/toe, high/low, impact X/Y, face contact, FPS, calibration and shot count; unavailable values shown as dashes, not invented.
- Session/club selection, dashboard navigation and clear connection/measurement provenance.
- Show planned camera setup, calibration and replay settings without implementing actual capture, calibration or persistence in this gate.
- Controls must be functional for UI-only navigation and local UI state; unavailable physical operations must be disabled and labeled.

## Scope and boundaries
Allowed: React/TypeScript/CSS visual components, UI-only interactions and accessibility, narrowly scoped automated tests and governance. No backend changes, camera capture, algorithms, real shot recording, dependency upgrades, EXE packaging or changes to other projects.

## Acceptance
1. Existing six panel titles and synthetic provenance preserved.
2. Planned visual fields, buttons, configuration affordances and disabled future features visible.
3. UI keyboard/accessibility semantics; responsive layout.
4. Build, lint, Prettier, unit and E2E CI checks pass on final immutable SHA.
5. Separate explicit approval required for Gate 07 closeout and Gate 08 opening.
