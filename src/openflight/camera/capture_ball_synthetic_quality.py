"""Gate 24: offline synthetic capture-impact result with quality assessment."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .capture_ball_synthetic_impact import calculate_capture_ball_synthetic_impact
from .checkerboard_calibration import CheckerboardCalibration
from .synthetic_face_polygon import SyntheticFacePolygon
from .synthetic_impact_pipeline import SyntheticImpactResult
from .synthetic_impact_quality import SyntheticImpactQuality, assess_synthetic_impact_quality
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class AssessedSyntheticCaptureImpact:
    """Synthetic result and its explicitly non-physical quality assessment."""

    impact: SyntheticImpactResult
    quality: SyntheticImpactQuality


def assess_capture_ball_synthetic_impact(  # pylint: disable=too-many-arguments
    calibration: CheckerboardCalibration,
    capture: TriggeredCapture,
    candidate_frame_index: int,
    landmarks_face_mm: np.ndarray,
    landmark_pixels_px: np.ndarray,
    polygon: SyntheticFacePolygon,
    *,
    ball_radius_mm: float,
    max_ball_residual_rad: float,
    max_face_rms_px: float,
    min_face_margin_px: float,
    contact_tolerance_mm: float,
    threshold: int,
    min_area_px: float,
    ball_border_margin_px: float,
    min_circularity: float = 0.0,
    face_observation_frame_index: int | None = None,
) -> AssessedSyntheticCaptureImpact:
    """Compose selected-frame contour, synthetic impact and quality reporting."""
    impact = calculate_capture_ball_synthetic_impact(
        calibration, capture, candidate_frame_index,
        landmarks_face_mm, landmark_pixels_px, polygon,
        ball_radius_mm=ball_radius_mm,
        max_ball_residual_rad=max_ball_residual_rad,
        max_face_rms_px=max_face_rms_px,
        min_face_margin_px=min_face_margin_px,
        contact_tolerance_mm=contact_tolerance_mm,
        threshold=threshold,
        min_area_px=min_area_px,
        ball_border_margin_px=ball_border_margin_px,
        min_circularity=min_circularity,
        face_observation_frame_index=face_observation_frame_index,
    )
    return AssessedSyntheticCaptureImpact(
        impact=impact,
        quality=assess_synthetic_impact_quality(impact),
    )
