"""Gate 20-24: single entry point for offline synthetic motion diagnostics.

Processes one immutable capture through image extraction, synthetic geometry,
temporal proximity, trend classification and safe UI serialization.
No physical impact event or real-world accuracy is established.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .checkerboard_calibration import CheckerboardCalibration
from .offline_capture_batch import capture_fingerprint
from .offline_dual_object_motion import (
    OfflineDualObjectMotion, assess_offline_dual_object_motion,
)
from .offline_dual_object_sequence import (
    OfflineDualObjectSequence, assess_synthetic_dual_object_sequence,
)
from .offline_motion_ui_payload import export_synthetic_motion_ui_payload
from .synthetic_face_polygon import SyntheticFacePolygon
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class OfflineMotionAnalysis:
    """Auditable synthetic observations and UI-ready diagnostics."""

    sequence: OfflineDualObjectSequence
    motion: OfflineDualObjectMotion
    ui_payload: dict
    physical_contact_confirmed: bool = False

    def __post_init__(self) -> None:
        if self.physical_contact_confirmed is not False:
            raise ValueError("offline synthetic analysis cannot confirm impact")


def analyze_offline_synthetic_motion(  # pylint: disable=too-many-arguments
    calibration: CheckerboardCalibration,
    capture: TriggeredCapture,
    frame_indices: tuple[int, ...],
    landmarks_face_mm: np.ndarray,
    polygon: SyntheticFacePolygon,
    *,
    ball_radius_mm: float,
    max_ball_residual_rad: float,
    max_face_rms_px: float,
    min_face_margin_px: float,
    contact_tolerance_mm: float,
    max_sensor_gap_ns: int,
    max_host_gap_ns: int,
    minimum_change_px: float = 0.5,
    threshold: int = 180,
    min_area_px: float = 100.,
    border_margin_px: int = 2,
    min_ball_circularity: float = 0.85,
    max_frames: int = 32,
) -> OfflineMotionAnalysis:
    """Run the full synthetic-only image-to-UI evidence path.

    Recheck exact source bytes before exporting any diagnostics. Capture
    changes invalidate the entire analysis instead of mixing observations.
    """
    sequence = assess_synthetic_dual_object_sequence(
        calibration, capture, frame_indices, landmarks_face_mm, polygon,
        ball_radius_mm=ball_radius_mm,
        max_ball_residual_rad=max_ball_residual_rad,
        max_face_rms_px=max_face_rms_px,
        min_face_margin_px=min_face_margin_px,
        contact_tolerance_mm=contact_tolerance_mm,
        threshold=threshold, min_area_px=min_area_px,
        border_margin_px=border_margin_px,
        min_ball_circularity=min_ball_circularity, max_frames=max_frames,
    )
    motion = assess_offline_dual_object_motion(
        capture, sequence, max_sensor_gap_ns=max_sensor_gap_ns,
        max_host_gap_ns=max_host_gap_ns,
        minimum_change_px=minimum_change_px,
    )
    payload = export_synthetic_motion_ui_payload(sequence, motion)
    if capture_fingerprint(capture) != sequence.source_capture_fingerprint:
        raise ValueError("capture changed during offline motion analysis")
    return OfflineMotionAnalysis(sequence, motion, payload)
