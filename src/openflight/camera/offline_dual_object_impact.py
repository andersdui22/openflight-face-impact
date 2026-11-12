"""Direct synthetic ball-and-face image to 3D impact geometry integration.

Unlike single-object extraction, both contours originate from the same image.
This cannot establish real-world object identity or physical contact time.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .checkerboard_calibration import CheckerboardCalibration
from .synthetic_dual_object_observation import (
    SyntheticDualObjectObservation, extract_synthetic_ball_and_face,
)
from .synthetic_face_polygon import SyntheticFacePolygon
from .synthetic_impact_pipeline import SyntheticImpactResult
from .synthetic_observed_impact import calculate_synthetic_observed_impact
from .synthetic_impact_quality import SyntheticImpactQuality, assess_synthetic_impact_quality
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class OfflineDualObjectImpact:
    """Evidence from one image, synthetic geometry and fail-closed quality."""

    observation: SyntheticDualObjectObservation
    impact: SyntheticImpactResult
    quality: SyntheticImpactQuality
    physical_contact_confirmed: bool = False

    def __post_init__(self) -> None:
        if self.physical_contact_confirmed is not False:
            raise ValueError("synthetic geometry cannot confirm physical contact")


def assess_synthetic_dual_object_impact(  # pylint: disable=too-many-arguments
    calibration: CheckerboardCalibration,
    capture: TriggeredCapture,
    frame_index: int,
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
) -> OfflineDualObjectImpact:
    """Calculate synthetic impact using the two shapes in the same frame.

    Shape ambiguity raises ValueError rather than silently choosing a contour.
    Geometry rejection is preserved in the typed impact/quality result.
    """
    observed = extract_synthetic_ball_and_face(
        capture, frame_index, image_size=calibration.image_size,
        threshold=threshold, min_area_px=min_area_px,
        border_margin_px=border_margin_px,
        min_ball_circularity=min_ball_circularity,
    )
    impact = calculate_synthetic_observed_impact(
        calibration, observed.ball_contour_px,
        landmarks_face_mm, observed.face.pixels_px, polygon,
        image_size=calibration.image_size,
        ball_radius_mm=ball_radius_mm,
        max_ball_residual_rad=max_ball_residual_rad,
        max_face_rms_px=max_face_rms_px,
        min_face_margin_px=min_face_margin_px,
        contact_tolerance_mm=contact_tolerance_mm,
        ball_border_margin_px=border_margin_px,
        capture=capture,
        candidate_frame_index=frame_index,
        observation_frame_index=observed.face.frame_index,
        require_observation_frame_identity=True,
        validate_frame_image=True,
    )
    return OfflineDualObjectImpact(
        observed, impact, assess_synthetic_impact_quality(impact),
    )
