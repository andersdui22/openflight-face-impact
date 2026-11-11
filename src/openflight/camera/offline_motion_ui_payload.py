"""Gate 24: safe JSON-compatible synthetic motion payload for future UI.

No physical impact coordinates, contact time or millimetre accuracy is
exported from image-space proximity alone.
"""

from __future__ import annotations

from .offline_dual_object_motion import OfflineDualObjectMotion
from .offline_dual_object_sequence import OfflineDualObjectSequence


def export_synthetic_motion_ui_payload(
    sequence: OfflineDualObjectSequence,
    motion: OfflineDualObjectMotion,
) -> dict:
    """Provide explicit statuses, provenance and image-space chart samples.

    UI consumers must label this as synthetic diagnostic evidence only.
    """
    if not isinstance(sequence, OfflineDualObjectSequence):
        raise ValueError("typed dual-object sequence required")
    if not isinstance(motion, OfflineDualObjectMotion):
        raise ValueError("typed motion evidence required")
    if (sequence.physical_contact_confirmed is not False
            or motion.physical_contact_confirmed is not False
            or motion.proximity.physical_contact_confirmed is not False
            or motion.trend.physical_contact_confirmed is not False):
        raise ValueError("cannot export physical contact from synthetic evidence")
    observed_indices = {index for index, _ in sequence.assessed}
    sample_indices = {sample.frame_index for sample in motion.proximity.samples}
    if not sample_indices.issubset(observed_indices):
        raise ValueError("motion samples do not match observed frames")
    if (motion.trend.has_observed_approach_and_separation
            and motion.trend.closest_frame_index not in sample_indices):
        raise ValueError("motion trend references missing frame")
    return {
        "schema_version": 1,
        "kind": "synthetic_image_space_motion",
        "source_capture_fingerprint": sequence.source_capture_fingerprint,
        "physical_contact_confirmed": False,
        "impact_frame_index": None,
        "impact_x_mm": None,
        "impact_y_mm": None,
        "position_uncertainty_mm": None,
        "closest_observed_frame_index": motion.trend.closest_frame_index,
        "has_observed_approach_and_separation": (
            motion.trend.has_observed_approach_and_separation
        ),
        "motion_reason": motion.trend.reason,
        "proximity_reason": motion.proximity.reason,
        "observed_frame_indices": sorted(observed_indices),
        "rejected_frames": [
            {"frame_index": index, "reason": reason}
            for index, reason in sequence.rejected
        ],
        "proximity_samples": [
            {
                "frame_index": sample.frame_index,
                "sensor_timestamp_ns": sample.sensor_timestamp_ns,
                "host_timestamp_ns": sample.host_timestamp_ns,
                "separation_px": sample.separation_px,
            }
            for sample in motion.proximity.samples
        ],
    }
