"""Gate 20: bounded offline silhouette extraction from one grayscale image.

An explicitly supplied intensity threshold is required. This is not a
physically validated ball classifier or contact-frame detector.
"""

from __future__ import annotations

import cv2 as cv
import numpy as np

from .ball_contour_quality import validate_ball_contour_pixels


def extract_single_bright_contour(
    image: np.ndarray,
    *,
    threshold: int,
    min_area_px: float,
    border_margin_px: float,
) -> np.ndarray:
    """Extract exactly one closed bright foreground component, or reject."""
    pixels = np.asarray(image)
    if pixels.ndim != 2 or pixels.dtype != np.uint8:
        raise ValueError("contour image must be 2D uint8 grayscale")
    if pixels.shape[0] < 3 or pixels.shape[1] < 3:
        raise ValueError("contour image is too small")
    if not isinstance(threshold, int) or isinstance(threshold, bool) or not 0 <= threshold <= 254:
        raise ValueError("contour threshold must be integer 0..254")
    if (
        not isinstance(min_area_px, (int, float, np.integer, np.floating))
        or isinstance(min_area_px, (bool, np.bool_))
        or not np.isfinite(min_area_px)
        or min_area_px <= 0
    ):
        raise ValueError("contour minimum area must be finite and positive")
    _, binary = cv.threshold(pixels, threshold, 255, cv.THRESH_BINARY)
    contours, _ = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    candidates = [contour for contour in contours if cv.contourArea(contour) >= min_area_px]
    if len(candidates) != 1:
        raise ValueError("contour requires exactly one sufficiently large bright component")
    contour = candidates[0].reshape(-1, 2)
    return validate_ball_contour_pixels(
        contour, image_size=(pixels.shape[1], pixels.shape[0]),
        border_margin_px=border_margin_px,
    )
