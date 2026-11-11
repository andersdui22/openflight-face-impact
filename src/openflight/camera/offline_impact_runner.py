"""Explicit offline capture -> geometry -> timing -> targeted UI event pipeline.

The caller supplies synthetic face landmarks. No automatic camera face
detection, physical contact measurement, or background capture is implied.
"""

from __future__ import annotations

from .offline_capture_batch import assess_offline_capture_batch
from .offline_impact_handoff import prepare_offline_impact_handoff
from .offline_impact_transport import publish_offline_impact_handoff


def analyze_and_publish_offline_capture(  # pylint: disable=too-many-arguments
    calibration,
    capture,
    candidates,
    landmarks_face_mm,
    polygon,
    *,
    ball_radius_mm,
    max_ball_residual_rad,
    max_face_rms_px,
    min_face_margin_px,
    contact_tolerance_mm,
    threshold,
    min_area_px,
    ball_border_margin_px,
    max_sensor_gap_ns,
    max_host_gap_ns,
    emit,
    recipient,
    min_circularity=0.0,
    max_candidates=32,
):
    """Run actual offline assessments and emit only audited typed evidence.

    Exceptions abort before emission; there is no unverified fallback marker.
    This entry point must be invoked by a trusted server-side producer.
    """
    if not callable(emit):
        raise ValueError("offline event emitter must be callable")
    if not isinstance(recipient, str) or not recipient.strip():
        raise ValueError("offline event requires explicit recipient")
    batch = assess_offline_capture_batch(
        calibration, capture, candidates, landmarks_face_mm, polygon,
        ball_radius_mm=ball_radius_mm,
        max_ball_residual_rad=max_ball_residual_rad,
        max_face_rms_px=max_face_rms_px,
        min_face_margin_px=min_face_margin_px,
        contact_tolerance_mm=contact_tolerance_mm,
        threshold=threshold,
        min_area_px=min_area_px,
        ball_border_margin_px=ball_border_margin_px,
        min_circularity=min_circularity,
        max_candidates=max_candidates,
    )
    handoff = prepare_offline_impact_handoff(
        capture, batch,
        max_sensor_gap_ns=max_sensor_gap_ns,
        max_host_gap_ns=max_host_gap_ns,
        max_frames=max_candidates,
    )
    return publish_offline_impact_handoff(handoff, emit, recipient=recipient)
