"""Gate 20/22/23: selected-frame ball contour into synthetic impact geometry.

Face landmarks remain explicitly supplied synthetic observations. Their
pixel provenance and the physical contact instant are not established here.
"""

from __future__ import annotations

import numpy as np

from .capture_ball_contour import extract_capture_ball_contour
from .checkerboard_calibration import CheckerboardCalibration
from .synthetic_face_polygon import SyntheticFacePolygon
from .synthetic_impact_pipeline import SyntheticImpactResult, SyntheticImpactStatus
from .synthetic_observed_impact import calculate_synthetic_observed_impact
from .triggered_buffer import TriggeredCapture


def calculate_capture_ball_synthetic_impact(  # pylint: disable=too-many-arguments
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
) -> SyntheticImpactResult:
    """Evaluate image-derived ball contour with externally supplied face pixels.

    This is an offline synthetic geometry integration, not a physical
    impact-time detector or independently verified face observation.
    Optional face frame identity checks caller metadata, not pixel provenance.
    """
    try:
        if face_observation_frame_index is not None:
            if (not isinstance(face_observation_frame_index, int)
                    or isinstance(face_observation_frame_index, bool)
                    or face_observation_frame_index != candidate_frame_index):
                raise ValueError("face observation frame index differs from candidate frame")
        observation = extract_capture_ball_contour(
            capture,
            candidate_frame_index,
            image_size=calibration.image_size,
            threshold=threshold,
            min_area_px=min_area_px,
            border_margin_px=ball_border_margin_px,
            min_circularity=min_circularity,
        )
    except (ValueError, TypeError, OverflowError) as error:
        return SyntheticImpactResult(
            SyntheticImpactStatus.INVALID_GEOMETRY, rejection_reason=str(error),
        )
    return calculate_synthetic_observed_impact(
        calibration,
        observation.contour_px,
        landmarks_face_mm,
        landmark_pixels_px,
        polygon,
        image_size=calibration.image_size,
        ball_radius_mm=ball_radius_mm,
        max_ball_residual_rad=max_ball_residual_rad,
        max_face_rms_px=max_face_rms_px,
        min_face_margin_px=min_face_margin_px,
        contact_tolerance_mm=contact_tolerance_mm,
        ball_border_margin_px=ball_border_margin_px,
        capture=capture,
        candidate_frame_index=candidate_frame_index,
        observation_frame_index=observation.frame_index,
        require_observation_frame_identity=True,
        validate_frame_image=True,
    )
