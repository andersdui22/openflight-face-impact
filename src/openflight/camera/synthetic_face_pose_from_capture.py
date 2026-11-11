"""Strict synthetic image-derived face-corner to existing pose-solver bridge.

No camera reader, new PnP solver, real clubface detection, or contact inference.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .checkerboard_calibration import CheckerboardCalibration
from .synthetic_face_landmark_pose import FaceLandmarkPose, estimate_synthetic_face_pose
from .synthetic_face_pixel_observation import (
    SyntheticFacePixelObservation, extract_synthetic_face_corners,
)
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class SyntheticObservedFacePose:
    """Image-provenanced synthetic corners and existing planar pose result."""

    observation: SyntheticFacePixelObservation
    pose: FaceLandmarkPose


def estimate_capture_synthetic_face_pose(  # pylint: disable=too-many-arguments
    calibration: CheckerboardCalibration,
    capture: TriggeredCapture,
    frame_index: int,
    landmarks_face_mm: np.ndarray,
    *,
    threshold: int = 180,
    max_rms_px: float,
    min_margin_px: float,
    landmark_border_margin_px: float = 0.0,
) -> SyntheticObservedFacePose:
    """Extract synthetic rectangular corners and reuse the existing pose solver.

    Fails closed for unobservable planar pose or ambiguous image fixture.
    No output is emitted when pose acceptance fails.
    """
    observation = extract_synthetic_face_corners(
        capture, frame_index, image_size=calibration.image_size,
        threshold=threshold,
    )
    pose = estimate_synthetic_face_pose(
        calibration, landmarks_face_mm, observation.pixels_px,
        image_size=calibration.image_size,
        max_rms_px=max_rms_px,
        min_margin_px=min_margin_px,
        landmark_border_margin_px=landmark_border_margin_px,
    )
    return SyntheticObservedFacePose(observation=observation, pose=pose)
