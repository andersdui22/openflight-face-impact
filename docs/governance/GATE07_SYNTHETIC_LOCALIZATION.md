# Gate 07 — Synthetic ball and clubface localization

Status: ACTIVE, explicitly approved by user ("Godkendt") on 2026-11-08 following Gate 06 same-SHA CI closeout.

Project Law V1 unchanged. Base: Gate 06 `9522651a6a4be988f8bd8da22447b50cf1779099`, draft PR #6 unmerged, all six GitHub CI workflows successful. Gate 04 physical ELP validation remains deferred.

## Evidence and reuse decision

Existing `src/openflight/camera/detector.py::BallDetector` uses OpenCV Hough circles and assumes IR-illuminated bright balls against dark backgrounds; it is not established for ELP OV9281 or synthetic colored annotations. Existing Gate 06 frame validation and Gate 05 pixel/mm calibration are available but do not locate objects. No suitable existing synthetic two-class marker locator was found in reviewed camera modules. Avoid modifying the legacy detector or adding a parallel acquisition pipeline.

## Approved implementation

Implement a small hardware-free, pure NumPy locator for **explicitly color-coded synthetic RGB test images** containing one annotated circular ball and one annotated rectangular clubface. Return their pixel-space centers and bounding boxes, and fail closed for missing, ambiguous, malformed or geometrically invalid objects. Reuse existing conventions (column,row), avoid inventing physical confidence scores. Add tests for deterministic positions and invalid/ambiguous cases, documentation and CI.

## Acceptance and exclusions

Tests show accurate synthetic marker localization with known pixel geometry; absence, multiple disconnected markers, invalid frame shapes and malformed masks must be rejected. No real-image object recognition, no camera hardware, Face Impact contact computation, millimeter accuracy claim, physical testing, club motion metrics, UI change, merge, release or Golden baseline. A color-coded synthetic test fixture is **not evidence** that natural golf balls or clubfaces can be detected in actual ELP footage.
