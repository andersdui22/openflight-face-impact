# Preparatory software work for Gates 25–30

This is **not** an assertion of the canonical Gate 25–30 names or acceptance criteria. The canonical MDP V1.2 file has not been located in the inspected GitHub tree. Reconcile gate definitions before marking any Gate completed.

## Parallel tracks
- Track A: continue outstanding Gates 20–24 acceptance evidence, UI formatting, authentic screenshot, Windows Python backend startup and packaging CI.
- Track B: implement isolated, testable software prerequisites for subsequent camera/impact gates. Do not infer camera accuracy or contact location from synthetic frame statistics.
- Track C: defer real ELP OV9281 physical capture, exposure/fps characterization, club calibration and accuracy tests until software gates are as complete as possible.

## First preparatory deliverable
`offline_frame_quality.py` reports basic 8-bit grayscale frame dimensions, brightness, saturation, darkness and robust contrast. `require_usable_offline_frame` rejects obviously unusable frames without producing face impact measurements. Tests use synthetic arrays only. No live camera connection, gate closure, UI integration, merge or release is implied.

## Remaining acceptance blockers
The frame quality thresholds are provisional software safeguards, not calibrated physical limits. Validate with actual ELP frames later. Confirm canonical MDP Gate 25–30 criteria and ensure dependencies are satisfied before any gate-specific sign-off.
