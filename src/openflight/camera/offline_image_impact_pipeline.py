"""Software-only Gate 20-24 image observation to synthetic impact assessment.

This adapter does not identify real clubfaces or physical contact frames.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .checkerboard_calibration import CheckerboardCalibration
from .offline_capture_batch import OfflineCaptureBatchResult, assess_offline_capture_batch
from .offline_face_observation_batch import (
    OfflineFaceObservationBatch, observe_synthetic_face_frames,
)
from .synthetic_face_polygon import SyntheticFacePolygon
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class OfflineImageImpactResult:
    """Image observations, explicit failures and assessed synthetic frames."""

    observations: OfflineFaceObservationBatch
    assessment: OfflineCaptureBatchResult | None
    physical_contact_confirmed: bool = False

    def __post_init__(self) -> None:
        if self.physical_contact_confirmed is not False:
            raise ValueError("image-only synthetic analysis cannot confirm contact")


def assess_image_derived_synthetic_impact(  # pylint: disable=too-many-arguments
    calibration: CheckerboardCalibration,
    capture: TriggeredCapture,
    frame_indices: tuple[int, ...],
    landmarks_face_mm: np.ndarray,
    polygon: SyntheticFacePolygon,
    *,
    image_size: tuple[int, int],
    face_threshold: int = 180,
    face_min_area_px: float = 100.0,
    face_min_fill_ratio: float = 0.85,
    face_border_margin_px: int = 2,
    ball_radius_mm: float,
    max_ball_residual_rad: float,
    max_face_rms_px: float,
    min_face_margin_px: float,
    contact_tolerance_mm: float,
    ball_threshold: int,
    ball_min_area_px: float,
    ball_border_margin_px: float,
    min_circularity: float = 0.0,
    max_frames: int = 32,
) -> OfflineImageImpactResult:
    """Observe each requested image, then assess only accepted face fixtures.

    Zero accepted observations yields no assessment, never fabricated impact.
    Ambiguous accepted frames remain distinct; this does not select contact.
    """
    observations = observe_synthetic_face_frames(
        capture, frame_indices, image_size=image_size,
        threshold=face_threshold, min_area_px=face_min_area_px,
        min_fill_ratio=face_min_fill_ratio,
        border_margin_px=face_border_margin_px, max_frames=max_frames,
    )
    if not observations.candidates:
        return OfflineImageImpactResult(observations, None)
    assessment = assess_offline_capture_batch(
        calibration, capture, observations.candidates,
        landmarks_face_mm, polygon,
        ball_radius_mm=ball_radius_mm,
        max_ball_residual_rad=max_ball_residual_rad,
        max_face_rms_px=max_face_rms_px,
        min_face_margin_px=min_face_margin_px,
        contact_tolerance_mm=contact_tolerance_mm,
        threshold=ball_threshold, min_area_px=ball_min_area_px,
        ball_border_margin_px=ball_border_margin_px,
        min_circularity=min_circularity, max_candidates=max_frames,
    )
    return OfflineImageImpactResult(observations, assessment)
