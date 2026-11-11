"""Gate 20-24 bounded multi-frame synthetic ball/face analysis.

Each frame is assessed independently. Neither a best contact frame nor
physical club/ball identity is inferred from a sequence of bright shapes.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .checkerboard_calibration import CheckerboardCalibration
from .offline_capture_batch import capture_fingerprint
from .offline_dual_object_impact import (
    OfflineDualObjectImpact, assess_synthetic_dual_object_impact,
)
from .synthetic_face_polygon import SyntheticFacePolygon
from .synthetic_impact_pipeline import SyntheticImpactStatus
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class OfflineDualObjectSequence:
    """Per-frame evidence, explicit rejections and source provenance."""

    assessed: tuple[tuple[int, OfflineDualObjectImpact], ...]
    rejected: tuple[tuple[int, str], ...]
    source_capture_fingerprint: str
    physical_contact_confirmed: bool = False

    def __post_init__(self) -> None:
        if self.physical_contact_confirmed is not False:
            raise ValueError("synthetic sequence cannot confirm contact")

    @property
    def accepted_synthetic_frame_indices(self) -> tuple[int, ...]:
        """Report accepted synthetic geometry without choosing a contact frame."""
        return tuple(index for index, item in self.assessed
                     if item.impact.status is SyntheticImpactStatus.OK)


def assess_synthetic_dual_object_sequence(  # pylint: disable=too-many-arguments
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
    threshold: int = 180,
    min_area_px: float = 100.,
    border_margin_px: int = 2,
    min_ball_circularity: float = 0.85,
    max_frames: int = 32,
) -> OfflineDualObjectSequence:
    """Process distinct selected frames and retain all synthetic outcomes.

    Shape extraction failures are recorded per frame; geometry failures remain
    typed assessed results. Capture mutation during analysis aborts the batch.
    """
    if (type(max_frames) is not int or max_frames <= 0
            or not isinstance(frame_indices, tuple)
            or not 0 < len(frame_indices) <= max_frames
            or any(type(i) is not int or i < 0 or i >= len(capture.frames)
                   for i in frame_indices)
            or len(set(frame_indices)) != len(frame_indices)):
        raise ValueError("frame indices must be distinct, bounded and within capture")
    source_fingerprint = capture_fingerprint(capture)
    assessed = []
    rejected = []
    for index in frame_indices:
        try:
            result = assess_synthetic_dual_object_impact(
                calibration, capture, index, landmarks_face_mm, polygon,
                ball_radius_mm=ball_radius_mm,
                max_ball_residual_rad=max_ball_residual_rad,
                max_face_rms_px=max_face_rms_px,
                min_face_margin_px=min_face_margin_px,
                contact_tolerance_mm=contact_tolerance_mm,
                threshold=threshold, min_area_px=min_area_px,
                border_margin_px=border_margin_px,
                min_ball_circularity=min_ball_circularity,
            )
        except ValueError as error:
            rejected.append((index, str(error)))
            continue
        assessed.append((index, result))
    if capture_fingerprint(capture) != source_fingerprint:
        raise ValueError("capture changed during dual-object sequence assessment")
    return OfflineDualObjectSequence(
        tuple(assessed), tuple(rejected), source_fingerprint,
    )
