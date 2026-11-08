# Gate 06 — Synthetic frame/calibration integration

Status: ACTIVE; explicitly approved by user ("Godkendt") after the 2026-11-08 proposal.

Project Law: V1. Base: Gate 05 branch commit `631c7bbb008da94c13a42c8596e4c7a9e589eb80`, draft PR #5, six of six workflows successful on that exact SHA. Gate 04 physical camera validation remains deferred.

## Problem and evidence

Gate 05 supplies a pure `SyntheticPlanarCalibration` Nx2 pixel-to-mm affine transform and hardware-free tests, but no image-frame boundary or integration of known synthetic image points. Reuse the existing pure transform; do not duplicate camera capture or infer image detections. Existing OpenFlight camera acquisition and React/Electron UI are unchanged.

## Allowed changes

Add a minimal pure Python adapter accepting an explicitly supplied synthetic image frame and known Nx2 pixel coordinates, checking frame dimensions, point bounds and finite coordinates, and applying the existing Gate 05 mapping. Add hardware-free tests, documentation, governance and CI. Use explicit image row/column and planar millimeter conventions.

## Acceptance

Valid synthetic frames and supplied pixel points produce deterministic mm coordinates; invalid frame shapes, out-of-bounds points and invalid values fail closed. Existing Gate 05 calibration remains authoritative. Applicable CI succeeds on the final exact SHA.

## Exclusions and stop conditions

No camera hardware, live feed, automatic ball/clubface detection, contact-frame selection, Face Impact solver, physical accuracy claim, Club Path/AoA/speed, UI redesign, ConnectorNext/MLM2PRO/BLE/radar, merge, release or Golden nomination. Stop before any such work or if evidence is insufficient.
