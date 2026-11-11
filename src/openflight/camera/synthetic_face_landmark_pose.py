"""Estimate the pose of a synthetic planar clubface from labelled pixels."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .calibrated_rays import calibrated_pixel_rays
from .checkerboard_calibration import CheckerboardCalibration
from .synthetic_mesh_pose import SyntheticPoseCandidate


@dataclass(frozen=True)
class FaceLandmarkPose:
    """Face-local to camera pose, with a pixel-domain fit diagnostic."""

    pose_model_to_camera: SyntheticPoseCandidate
    rms_px: float
    runner_up_rms_px: float | None


def _plane_points(landmarks: np.ndarray) -> np.ndarray:
    points = np.asarray(landmarks)
    if points.ndim != 2 or points.shape[1] != 2 or len(points) < 4:
        raise ValueError("at least four planar landmarks are required")
    if points.dtype.kind not in "iuf" or not np.all(np.isfinite(points)):
        raise ValueError("face landmarks must be finite numeric millimetres")
    if len(np.unique(points, axis=0)) != len(points):
        raise ValueError("face landmarks must be distinct")
    points = points.astype(np.float64)
    _require_planar_spread(points)
    return np.column_stack((points, np.zeros(len(points))))


def _require_planar_spread(points: np.ndarray) -> None:
    singular = np.linalg.svd(points - points.mean(axis=0), compute_uv=False)
    if singular[1] <= singular[0] * 1e-3:
        raise ValueError("landmarks do not provide enough planar spread")


def _score_candidate(cv, objects, pixels, calibration, vectors):
    rvec, tvec = vectors
    rotation, _ = cv.Rodrigues(rvec)
    translation = tvec.reshape(3)
    if not np.all(np.isfinite(rotation)) or not np.all(np.isfinite(translation)):
        return None
    depths = objects @ rotation[2] + translation[2]
    # The model's +z is the visible face normal.
    if np.any(depths <= 0) or rotation[:, 2] @ translation >= 0:
        return None
    reprojection, _ = cv.projectPoints(
        objects, rvec, tvec, calibration.camera_matrix, calibration.distortion
    )
    errors = reprojection.reshape(-1, 2) - pixels
    rms = float(np.sqrt(np.mean(np.sum(errors**2, axis=1))))
    if not math.isfinite(rms):
        return None
    return rms, SyntheticPoseCandidate(rotation, translation)


def estimate_synthetic_face_pose(  # pylint: disable=too-many-arguments
    calibration: CheckerboardCalibration,
    landmarks_face_mm: np.ndarray,
    pixels_px: np.ndarray,
    *,
    image_size: tuple[int, int],
    max_rms_px: float,
    min_margin_px: float,
    landmark_border_margin_px: float = 0.0,
) -> FaceLandmarkPose:
    """Solve a labelled planar face in the optical right/down/forward frame.

    Landmarks are ordered (heel-to-toe, bottom-to-top) millimetres on z=0.
    The corresponding pixels use the same order. The returned rigid pose
    uses camera coordinates as the world frame of SyntheticPoseCandidate.
    Both the acceptance limit and the required score gap are in pixels.
    """
    # pylint: disable=no-member
    import cv2 as cv  # pylint: disable=import-outside-toplevel

    if not all(
        isinstance(limit, (int, float, np.integer, np.floating))
        and not isinstance(limit, (bool, np.bool_))
        and math.isfinite(limit)
        and limit > 0
        for limit in (max_rms_px, min_margin_px)
    ):
        raise ValueError("pose score thresholds must be positive and finite")

    if (
        not isinstance(landmark_border_margin_px, (int, float, np.integer, np.floating))
        or isinstance(landmark_border_margin_px, (bool, np.bool_))
        or not math.isfinite(landmark_border_margin_px)
        or landmark_border_margin_px < 0
    ):
        raise ValueError("landmark border margin must be finite and nonnegative")

    objects = _plane_points(landmarks_face_mm)
    pixels = np.asarray(pixels_px)
    if pixels.shape != (len(objects), 2):
        raise ValueError("each planar landmark requires a corresponding pixel")
    rays = calibrated_pixel_rays(calibration, pixels, image_size=image_size)
    if (
        np.any(pixels < landmark_border_margin_px)
        or np.any(pixels >= np.asarray(image_size) - landmark_border_margin_px)
    ):
        raise ValueError("face landmark is inside the excluded image border")
    normalized = rays[:, :2] / rays[:, 2, None]
    if len(np.unique(pixels, axis=0)) != len(pixels):
        raise ValueError("observed pixels must be distinct")
    _require_planar_spread(normalized)

    try:
        count, rotations, translations, _ = cv.solvePnPGeneric(
            objects, normalized, np.eye(3), None, flags=cv.SOLVEPNP_IPPE
        )
        candidates = []
        if count:
            for vectors in zip(rotations, translations):
                score = _score_candidate(cv, objects, pixels, calibration, vectors)
                if score is not None:
                    candidates.append(score)
    except cv.error as error:
        raise ValueError("OpenCV could not estimate a planar face pose") from error
    candidates.sort(key=lambda candidate: candidate[0])
    if not candidates or candidates[0][0] > max_rms_px:
        raise ValueError("no face pose satisfies the reprojection limit")
    best_rms, best_pose = candidates[0]
    runner_up = candidates[1][0] if len(candidates) > 1 else None
    if runner_up is not None and runner_up - best_rms < min_margin_px:
        raise ValueError("ambiguous planar face pose")
    return FaceLandmarkPose(best_pose, best_rms, runner_up)
