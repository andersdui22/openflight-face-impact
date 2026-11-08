# Gate 09 — Synthetic dual-object detection pipeline

Status: ACTIVE; explicitly approved by user ("Godkendt", 2026-11-08).
Base: Gate 08 `1bd4ad2919b4817cf3a6a8017f2b4d241684c9ff`, six of six CI successful, draft PR #8 unmerged.
Project Law V1 remains unchanged.

## Problem and evidence

The existing `BallDetector.detect(CapturedFrame)` finds a bright circular ball via OpenCV. Gate 08 `locate_synthetic_ir_face` identifies an exactly rectangular bright marker in a **face-only grayscale crop**. Neither identifies the clubface in an unannotated natural scene. These outputs are currently separate. We need an isolated, hardware-free orchestration step with explicit fixture inputs and coordinate mapping, not a new detector or a Face Impact estimate.

## Approved implementation

- Add one small pure synthetic pipeline that accepts a full-frame uint8 grayscale fixture and an explicitly supplied face crop bounding box, reuses the unchanged ball detector and synthetic face locator, and maps the face crop's local pixel coordinates to full-frame pixels.
- Return both detections with clearly named image-pixel coordinates and input frame metadata; reject missing ball, missing face, malformed/out-of-bounds crop, overlap or ambiguous markers. Do not infer face crop position from the image.
- Add deterministic synthetic tests for success and fail-closed cases. Update Handoff and verify all six same-SHA CI workflows.

## Exclusions and stop conditions

No real camera or physical test, natural-image face detection, automatic region proposal, club pose, impact location, mm accuracy, UI integration, merge, release or Golden baseline. A face-only crop is an externally supplied synthetic annotation, not measured geometry. Stop on an unexpected source contract or failed CI until investigated.
