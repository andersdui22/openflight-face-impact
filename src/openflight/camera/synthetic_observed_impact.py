"""Compose supplied synthetic image observations into a face contact result."""

import numpy as np

from .ball_contour_quality import validate_ball_contour_pixels
from .ball_silhouette_range import estimate_ball_position
from .calibrated_rays import calibrated_pixel_rays
from .checkerboard_calibration import CheckerboardCalibration
from .synthetic_face_frame import SyntheticFaceFrame
from .synthetic_face_landmark_pose import estimate_synthetic_face_pose
from .synthetic_face_polygon import SyntheticFacePolygon
from .trigger_timing_quality import validate_candidate_frame_index
from .triggered_buffer import TriggeredCapture
from .synthetic_impact_pipeline import (
    SyntheticImpactResult,
    SyntheticImpactStatus,
    calculate_synthetic_face_impact,
)


def calculate_synthetic_observed_impact(  # pylint: disable=too-many-arguments
    calibration: CheckerboardCalibration,
    ball_edge_pixels_px: np.ndarray,
    landmarks_face_mm: np.ndarray,
    landmark_pixels_px: np.ndarray,
    polygon: SyntheticFacePolygon,
    *,
    image_size: tuple[int, int],
    ball_radius_mm: float,
    max_ball_residual_rad: float,
    max_face_rms_px: float,
    min_face_margin_px: float,
    contact_tolerance_mm: float,
    ball_border_margin_px: float = 0.0,
    capture: TriggeredCapture | None = None,
    candidate_frame_index: int | None = None,
    observation_frame_index: int | None = None,
) -> SyntheticImpactResult:
    """Evaluate one supplied synthetic candidate frame in camera millimetres.

    Both pixel sets share a calibrated image and instant. Landmark and polygon
    coordinates share a face-local origin and axes. The caller must supply
    all thresholds; this function does not determine the contact instant.
    An optional capture/index pair checks provenance. If supplied, the explicit\n    observation frame index must match the candidate; this verifies caller\n    metadata consistency, not the image contents or physical contact instant.
    """
    try:
        if image_size != calibration.image_size:
            raise ValueError("image dimensions must match the calibration")
        if capture is None and candidate_frame_index is not None:
            raise ValueError("candidate frame index requires a capture")
        if capture is not None:
            validate_candidate_frame_index(capture, candidate_frame_index)
        if observation_frame_index is not None:
            if capture is None:
                raise ValueError("observation frame index requires a capture")
            validate_candidate_frame_index(capture, observation_frame_index)
            if observation_frame_index != candidate_frame_index:
                raise ValueError("observation frame index differs from candidate frame")
        contour = validate_ball_contour_pixels(
            ball_edge_pixels_px,
            image_size=image_size,
            border_margin_px=ball_border_margin_px,
        )
        rays = calibrated_pixel_rays(calibration, contour, image_size=image_size)
        ball = estimate_ball_position(
            rays,
            radius_mm=ball_radius_mm,
            max_residual_rad=max_ball_residual_rad,
        )
        face = estimate_synthetic_face_pose(
            calibration,
            landmarks_face_mm,
            landmark_pixels_px,
            image_size=image_size,
            max_rms_px=max_face_rms_px,
            min_margin_px=min_face_margin_px,
        )
    except (ValueError, TypeError, OverflowError) as error:
        return SyntheticImpactResult(
            SyntheticImpactStatus.INVALID_GEOMETRY, rejection_reason=str(error)
        )

    frame = SyntheticFaceFrame(np.zeros(3), *np.eye(3))
    return calculate_synthetic_face_impact(
        ball.center_camera_mm,
        ball_radius_mm,
        frame,
        face.pose_model_to_camera,
        polygon,
        tolerance_mm=contact_tolerance_mm,
    )
