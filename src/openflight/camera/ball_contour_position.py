"""Gate 20: compose one offline bright contour with calibrated ball rays."""

from __future__ import annotations

import numpy as np

from .ball_contour_extraction import extract_single_bright_contour
from .ball_silhouette_range import BallSilhouettePosition, estimate_ball_position
from .calibrated_rays import calibrated_pixel_rays
from .checkerboard_calibration import CheckerboardCalibration


def estimate_bright_ball_position(
    calibration: CheckerboardCalibration,
    image: np.ndarray,
    *,
    threshold: int,
    min_area_px: float,
    border_margin_px: float,
    ball_radius_mm: float,
    max_ball_residual_rad: float,
    min_circularity: float = 0.0,
) -> BallSilhouettePosition:
    """Estimate a synthetic candidate sphere from one grayscale silhouette.

    Brightness alone cannot identify a golf ball; physical range accuracy is
    not established by this image-domain and ray-geometry composition.
    """
    pixels = np.asarray(image)
    if pixels.ndim != 2:
        raise ValueError("ball image must be 2D grayscale")
    image_size = (pixels.shape[1], pixels.shape[0])
    if image_size != calibration.image_size:
        raise ValueError("image dimensions must match the calibration")
    contour = extract_single_bright_contour(
        pixels,
        threshold=threshold,
        min_area_px=min_area_px,
        border_margin_px=border_margin_px,
        min_circularity=min_circularity,
    )
    rays = calibrated_pixel_rays(calibration, contour, image_size=image_size)
    return estimate_ball_position(
        rays, radius_mm=ball_radius_mm, max_residual_rad=max_ball_residual_rad,
    )
