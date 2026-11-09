# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 32

Title: Reference-inspired Face Impact dashboard UI
State: APPROVED — user explicitly approved "Gate 32 – Dashboard UI 1:1" on 2026-11-09.
Project Law: V1 unchanged.
Working branch: `gate32/face-impact-dashboard`.
Base: Gate 31 `cc6f2099f8bbdf2c0f678063fe07e74d492d1aa8`, seven successful same-SHA workflows, draft PR #31 unmerged.

## Authorized scope
Implement a close visual layout adaptation of the user-provided golf-analysis screenshot in the existing React UI: dark blue-gray compact navigation, left shot/session sidebar, six dashboard tiles, and a lower metrics strip. Use original CSS/SVG only, not copyrighted screenshots or proprietary assets. Reuse the existing FaceImpactView and SyntheticFaceImpactDemo. Show explicit unavailable states for metrics the single ELP camera cannot provide. Preserve the existing Live, Debug, Shots, Camera, Stats, Profiles flows, backend, and socket contracts.

## Acceptance
Responsive dashboard accessible in the real app; synthetic impact can be requested without misleading physical claims; legacy navigation remains available; automated UI build, lint, tests and browser smoke pass on the final SHA. The screenshot is a layout reference, not permission to invent sensor measurements.

## Exclusions and stop conditions
No physical camera testing, new measurement algorithms, backend or protocol changes, new dependencies, Windows packaging, merges, releases, Golden baselines, upstream repository changes or ConnectorNext work. Stop for any required scope expansion. Keep the PR draft and stacked on Gate 31.
