"""Apply a synthetic planar calibration to supplied pixel points in a frame.

No camera acquisition, image detection or physical accuracy is implied.
"""

from __future__ import annotations

import numpy as np

from openflight.camera.synthetic_calibration import SyntheticPlanarCalibration


def map_frame_points_to_millimeters(
    frame: np.ndarray,
    pixel_points: np.ndarray,
    calibration: SyntheticPlanarCalibration,
) -> np.ndarray:
    """Map known (column, row) pixel points in a synthetic frame to (x, y) mm.

    A frame has shape (height, width) or (height, width, channels), with
    positive dimensions; channels must be positive when present. Points are
    Nx2 finite pixel-center coordinates inside [0,width) x [0,height).
    The caller supplies the points: this function does not detect objects.
    """
    image = np.asarray(frame)
    if (
        image.ndim not in (2, 3)
        or image.shape[0] == 0
        or image.shape[1] == 0
        or (image.ndim == 3 and image.shape[2] == 0)
    ):
        raise ValueError("Expected a nonempty 2D or 3D image frame")
    points = np.asarray(pixel_points, dtype=float)
    if points.ndim != 2 or points.shape[1] != 2 or not np.isfinite(points).all():
        raise ValueError("Expected finite Nx2 (column, row) pixel points")
    height, width = image.shape[:2]
    if np.any(points < 0) or np.any(points[:, 0] >= width) or np.any(points[:, 1] >= height):
        raise ValueError("Pixel points must be inside the supplied frame")
    return calibration.to_millimeters(points)
