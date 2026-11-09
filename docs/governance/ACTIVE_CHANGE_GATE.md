# OPENFLIGHT FACE IMPACT — ACTIVE CHANGE GATE 18

Title: Integrated synthetic Face Impact calculation pipeline
State: ACTIVE — user explicitly approved "Godkendt" (2026-11-09).
Project Law: V1 unchanged.
Working branch: `gate18/synthetic-impact-pipeline`.
Base: Gate 17 `bb4b6338edbdb1c3135db5d4e01d2b7f38f81dbc`, six successful same-SHA workflows; draft PR #17 unmerged.

## Authorized scope
Provide a single synthetic calculation entry point that receives an explicitly known 3D ball center, radius, clubface frame, rigid pose and polygonal footprint; reuses Gate 17 and Gate 15 calculations; returns structured successful Face Impact X/Y in millimetres, heel/toe and high/low, or a structured rejection reason. Test success, transformed pose, outside footprint, non-tangency and invalid inputs. Preserve failure distinctions and do not fabricate measurements.

## Acceptance
Deterministic synthetic tests and six same-SHA CI successes. Clear result contract and rejection status.

## Exclusions
No camera integration, actual pose estimation, measured impact, physical test, radar, UI, merge, release or Golden baseline.
