"""Convert offline Brown-five pixel observations to optical unit rays.

Adapted from CalibratedProjection.pixel_rays_lfu and the Brown Jacobian in
HarjotDhanota/openflight ea95a64329e5bbea52f901e3badb1cb07995a6fc,
src/openflight/camera/calibrated_projection.py (AGPL-3.0-or-later).
"""

from __future__ import annotations

import numpy as np

from .checkerboard_calibration import CheckerboardCalibration


def _brown_jacobian_determinant(points: np.ndarray, coefficients: np.ndarray) -> np.ndarray:
    """Return the local area scale in normalized camera coordinates."""
    x, y = points.T
    k1, k2, p1, p2, k3 = coefficients
    radius2 = x**2 + y**2
    derivative = k1 + 2 * k2 * radius2 + 3 * k3 * radius2**2
    radial = 1 + k1 * radius2 + k2 * radius2**2 + k3 * radius2**3
    dx_dx = radial + 2 * x**2 * derivative + 2 * p1 * y + 6 * p2 * x
    dy_dy = radial + 2 * y**2 * derivative + 6 * p1 * y + 2 * p2 * x
    off_diagonal = 2 * x * y * derivative + 2 * p1 * x + 2 * p2 * y
    return dx_dx * dy_dy - off_diagonal**2


def _validate_optics(calibration: CheckerboardCalibration) -> tuple[np.ndarray, np.ndarray]:
    matrix = np.asarray(calibration.camera_matrix, dtype=np.float64)
    distortion = np.asarray(calibration.distortion, dtype=np.float64)
    if matrix.shape != (3, 3) or not np.all(np.isfinite(matrix)):
        raise ValueError("camera matrix must be a finite 3x3 array")
    canonical = np.array(
        [[matrix[0, 0], 0, matrix[0, 2]], [0, matrix[1, 1], matrix[1, 2]], [0, 0, 1]]
    )
    if min(matrix[0, 0], matrix[1, 1]) <= 0 or not np.array_equal(matrix, canonical):
        raise ValueError("camera matrix must have canonical form and positive focal lengths")
    if distortion.shape != (5,) or not np.all(np.isfinite(distortion)):
        raise ValueError("distortion must contain five finite Brown coefficients")
    return matrix, distortion


def calibrated_pixel_rays(
    calibration: CheckerboardCalibration,
    pixels_px: np.ndarray,
    *,
    image_size: tuple[int, int],
) -> np.ndarray:
    """Return one unit direction per input pixel, in the same order.

    Image size is (width, height); observations are an (N, 2) array of
    (column, row). Rays originate at the camera, with +x right, +y down,
    and +z forward. A ray has no assigned depth.
    """
    # pylint: disable=no-member
    import cv2 as cv  # pylint: disable=import-outside-toplevel

    if (
        not isinstance(image_size, tuple)
        or len(image_size) != 2
        or any(not isinstance(size, int) or isinstance(size, bool) or size < 1
               for size in image_size)
        or image_size != calibration.image_size
    ):
        raise ValueError("image dimensions must match the calibration")
    pixels = np.asarray(pixels_px)
    if (
        pixels.ndim != 2
        or pixels.shape[1] != 2
        or not pixels.size
        or pixels.dtype.kind not in "iuf"
        or not np.all(np.isfinite(pixels))
    ):
        raise ValueError("pixels must be a nonempty array of finite column/row pairs")
    if np.any(pixels < 0) or np.any(pixels >= image_size):
        raise ValueError("pixel is outside the calibrated image")

    matrix, distortion = _validate_optics(calibration)
    pixels = np.ascontiguousarray(pixels, dtype=np.float64)
    criteria = (cv.TERM_CRITERIA_COUNT | cv.TERM_CRITERIA_EPS, 50, 1e-12)
    try:
        source = pixels.reshape(-1, 1, 2)
        if hasattr(cv, "undistortPointsIter"):
            normalized = cv.undistortPointsIter(source, matrix, distortion, None, None, criteria)
        else:
            normalized = cv.undistortPoints(source, matrix, distortion, criteria=criteria)
        normalized = normalized.reshape(-1, 2)
        if not np.all(np.isfinite(normalized)):
            raise ValueError("distortion inversion returned non-finite coordinates")
        rays = np.column_stack((normalized, np.ones(len(normalized))))
        zero = np.zeros(3)
        reprojection, _ = cv.projectPoints(rays, zero, zero, matrix, distortion)
    except cv.error as error:
        raise ValueError("OpenCV could not invert the calibrated distortion") from error

    with np.errstate(over="ignore", invalid="ignore"):
        residual = np.linalg.norm(reprojection.reshape(-1, 2) - pixels, axis=1)
        determinant = _brown_jacobian_determinant(normalized, distortion)
        norms = np.linalg.norm(rays, axis=1, keepdims=True)
    if np.any(~np.isfinite(residual)) or np.any(residual > 1e-6):
        raise ValueError("distortion inversion did not converge")
    if np.any(~np.isfinite(determinant)) or np.any(determinant <= 0):
        raise ValueError("distortion is locally folded at the requested pixel")
    if not np.all(np.isfinite(norms)):
        raise ValueError("calibrated camera ray is invalid")
    return rays / norms
