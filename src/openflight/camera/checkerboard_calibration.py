"""Fit a Brown-five camera model from offline grayscale checkerboard images.

Board grid, minimum split sizes and frozen-intrinsics validation are adapted
from HarjotDhanota/openflight ea95a64329e5bbea52f901e3badb1cb07995a6fc,
src/openflight/camera/checkerboard_calibration.py (AGPL-3.0-or-later).
"""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass

import numpy as np

MIN_FIT_VIEWS = 10
MIN_VALIDATION_VIEWS = 3


@dataclass(frozen=True)
class Checkerboard:
    """Inner corner counts and the known side length of one square."""

    columns: int
    rows: int
    square_size_mm: float

    def object_points(self) -> np.ndarray:
        """Return ordered inner corners in board-local millimetres."""
        if not isinstance(self.columns, int) or not isinstance(self.rows, int):
            raise ValueError("board corner counts must be integers")
        if min(self.columns, self.rows) < 3:
            raise ValueError("board requires at least three inner corners per axis")
        if not math.isfinite(self.square_size_mm) or self.square_size_mm <= 0:
            raise ValueError("board square size must be positive and finite")
        points = np.zeros((self.columns * self.rows, 3), np.float32)
        column_grid, row_grid = np.meshgrid(np.arange(self.columns), np.arange(self.rows))
        points[:, :2] = np.column_stack((column_grid.ravel(), row_grid.ravel()))
        points *= self.square_size_mm
        return points


@dataclass(frozen=True)
class CheckerboardCalibration:
    """Image-bound candidate parameters, with residuals measured in pixels."""

    image_size: tuple[int, int]
    camera_matrix: np.ndarray
    distortion: np.ndarray  # OpenCV order: k1, k2, p1, p2, k3.
    fit_rms_px: float
    validation_rms_px: tuple[float, ...]


def _detect_split(cv, images, board, image_size, seen):
    corners = []
    for index, image in enumerate(images):
        name = f"checkerboard image {index + 1}"
        if not isinstance(image, np.ndarray) or image.dtype != np.uint8:
            raise ValueError(f"{name} must be a uint8 grayscale image")
        if image.shape != image_size[::-1]:
            raise ValueError(f"{name} has a different size or is not grayscale")
        digest = hashlib.sha256(image.tobytes()).digest()
        if digest in seen:
            raise ValueError(f"{name} duplicates a checkerboard image")
        seen.add(digest)
        found, points = cv.findChessboardCornersSB(image, (board.columns, board.rows))
        if not found:
            raise ValueError(f"{name} has no complete checkerboard")
        corners.append(points.reshape(-1, 2))
    return corners


def _validate_pose_diversity(cv, rotations, translations):
    normals = np.array([cv.Rodrigues(rotation)[0][:, 2] for rotation in rotations])
    cosine = np.clip(normals @ normals.T, -1, 1)
    span = np.degrees(np.arccos(cosine)).max()
    distances = np.linalg.norm(np.asarray(translations).reshape(-1, 3), axis=1)
    if not np.isfinite(span) or not np.all(np.isfinite(distances)):
        raise ValueError("calibration produced invalid fit poses")
    if span < 10 or distances.min() <= 0 or distances.max() / distances.min() < 1.15:
        raise ValueError("fit views require more variation in board orientation and distance")


def _score_view(cv, objects, corners, matrix, distortion):
    # Solve only the held-out view's pose. The remaining corners score it.
    anchor = np.arange(len(objects)) % 3 != 1
    success, rotation, translation = cv.solvePnP(
        objects[anchor], corners[anchor], matrix, distortion
    )
    if not success or not np.all(np.isfinite(rotation)) or not np.all(np.isfinite(translation)):
        raise ValueError("validation view pose could not be estimated")
    rotation_matrix, _ = cv.Rodrigues(rotation)
    depths = (objects @ rotation_matrix[2]) + translation[2, 0]
    if np.any(depths <= 0):
        raise ValueError("validation checkerboard lies behind the camera")
    projected, _ = cv.projectPoints(objects[~anchor], rotation, translation, matrix, distortion)
    errors = projected.reshape(-1, 2) - corners[~anchor]
    return float(np.sqrt(np.mean(np.sum(errors**2, axis=1))))


def calibrate_checkerboard(
    board: Checkerboard,
    fit_images: list[np.ndarray],
    validation_images: list[np.ndarray],
    *,
    max_validation_rms_px: float,
) -> CheckerboardCalibration:
    """Fit on one image set and validate frozen intrinsics on separate images.

    The caller supplies a pixel-residual budget. Passing it qualifies the
    supplied image experiment only. No capture hardware or mode is inferred.
    """
    # OpenCV is optional and its members are supplied by the native extension.
    # pylint: disable=no-member
    import cv2 as cv  # pylint: disable=import-outside-toplevel

    if len(fit_images) < MIN_FIT_VIEWS or len(validation_images) < MIN_VALIDATION_VIEWS:
        raise ValueError("calibration requires at least 10 fit and 3 validation images")
    if not math.isfinite(max_validation_rms_px) or max_validation_rms_px <= 0:
        raise ValueError("validation RMS limit must be positive and finite")
    objects = board.object_points()
    first = fit_images[0]
    if not isinstance(first, np.ndarray) or first.ndim != 2 or not first.size:
        raise ValueError("fit images must be nonempty grayscale arrays")
    image_size = (first.shape[1], first.shape[0])
    seen = set()
    try:
        fit = _detect_split(cv, fit_images, board, image_size, seen)
        validation = _detect_split(cv, validation_images, board, image_size, seen)
        rms, matrix, distortion, rotations, translations = cv.calibrateCamera(
            [objects] * len(fit), fit, image_size, None, None,
            flags=cv.CALIB_FIX_K4 | cv.CALIB_FIX_K5 | cv.CALIB_FIX_K6,
        )
        distortion = distortion.reshape(-1)
        if (
            not math.isfinite(rms)
            or not np.all(np.isfinite(matrix))
            or min(matrix[0, 0], matrix[1, 1]) <= 0
            or distortion.size != 5
            or not np.all(np.isfinite(distortion))
        ):
            raise ValueError("calibration produced invalid camera parameters")
        _validate_pose_diversity(cv, rotations, translations)
        scores = tuple(
            _score_view(cv, objects, corners, matrix, distortion) for corners in validation
        )
    except cv.error as error:
        raise ValueError("OpenCV could not calibrate the checkerboard views") from error
    if any(not math.isfinite(score) or score > max_validation_rms_px for score in scores):
        raise ValueError("held-out checkerboard exceeds the validation RMS limit")
    return CheckerboardCalibration(image_size, matrix, distortion, float(rms), scores)
