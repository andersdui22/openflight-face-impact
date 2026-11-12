"""Gate 20: offline image-domain completeness checks for supplied ball rim pixels."""

from __future__ import annotations

import numpy as np


def validate_ball_contour_pixels(
    pixels_px: np.ndarray,
    *,
    image_size: tuple[int, int],
    border_margin_px: float,
) -> np.ndarray:
    """Return a copied contour only when its rim is inside the safe image area.

    This is not a pixel detector or a claim that a contour belongs to a ball.
    Sphere/rim coverage is checked separately by the calibrated ray solver.
    """
    if (
        not isinstance(image_size, tuple)
        or len(image_size) != 2
        or any(not isinstance(v, int) or isinstance(v, bool) or v <= 0
               for v in image_size)
    ):
        raise ValueError("image size must be positive integer width and height")
    if (
        not isinstance(border_margin_px, (int, float, np.integer, np.floating))
        or isinstance(border_margin_px, (bool, np.bool_))
        or not np.isfinite(border_margin_px)
        or border_margin_px < 0
        or border_margin_px * 2 >= min(image_size)
    ):
        raise ValueError("invalid contour border margin")
    pixels = np.asarray(pixels_px)
    if (
        pixels.ndim != 2 or pixels.shape[1] != 2 or len(pixels) < 5
        or pixels.dtype.kind not in "iuf"
        or not np.all(np.isfinite(pixels))
    ):
        raise ValueError("ball contour requires five finite pixel pairs")
    width, height = image_size
    margin = float(border_margin_px)
    if (
        np.any(pixels[:, 0] < margin)
        or np.any(pixels[:, 1] < margin)
        or np.any(pixels[:, 0] >= width - margin)
        or np.any(pixels[:, 1] >= height - margin)
    ):
        raise ValueError("ball contour touches or crosses image border margin")
    if len(np.unique(pixels, axis=0)) != len(pixels):
        raise ValueError("ball contour contains duplicate pixels")
    return np.array(pixels, dtype=np.float64, copy=True)
