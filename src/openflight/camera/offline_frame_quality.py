"""Software-only frame integrity checks for future ELP acquisition gates.

This is an independent preflight check, not physical camera validation.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class OfflineFrameQuality:
    """Observed image properties; never interpreted as impact accuracy."""

    width: int
    height: int
    brightness_mean: float
    saturated_fraction: float
    dark_fraction: float
    contrast_span: float


def inspect_offline_frame(image: np.ndarray) -> OfflineFrameQuality:
    """Reject invalid frames and report bounded 8-bit grayscale diagnostics.

    Colour images, malformed buffers and empty frames fail closed. Callers
    must not use these statistics as evidence of a real camera measurement.
    """
    if not isinstance(image, np.ndarray):
        raise ValueError("frame must be a numpy image")
    if image.ndim != 2 or image.dtype != np.uint8:
        raise ValueError("frame must be 8-bit grayscale")
    height, width = image.shape
    if height < 2 or width < 2:
        raise ValueError("frame dimensions must be at least 2x2")
    if not image.flags.c_contiguous:
        raise ValueError("frame buffer must be contiguous")
    values = image.astype(np.float64)
    return OfflineFrameQuality(
        width=width,
        height=height,
        brightness_mean=float(values.mean()),
        saturated_fraction=float(np.count_nonzero(image >= 250) / image.size),
        dark_fraction=float(np.count_nonzero(image <= 5) / image.size),
        contrast_span=float(np.percentile(values, 95) - np.percentile(values, 5)),
    )


def require_usable_offline_frame(
    image: np.ndarray,
    *,
    max_saturated_fraction: float = 0.95,
    max_dark_fraction: float = 0.95,
    min_contrast_span: float = 5.0,
) -> OfflineFrameQuality:
    """Fail closed on unusable synthetic/offline frames before feature extraction."""
    for name, value in (
        ("max_saturated_fraction", max_saturated_fraction),
        ("max_dark_fraction", max_dark_fraction),
    ):
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
            raise ValueError(f"{name} must be within [0, 1]")
    if (not isinstance(min_contrast_span, (int, float))
            or isinstance(min_contrast_span, bool)
            or not 0 <= min_contrast_span <= 255):
        raise ValueError("min_contrast_span must be within [0, 255]")
    quality = inspect_offline_frame(image)
    if quality.saturated_fraction > max_saturated_fraction:
        raise ValueError("frame is overexposed")
    if quality.dark_fraction > max_dark_fraction:
        raise ValueError("frame is underexposed")
    if quality.contrast_span < min_contrast_span:
        raise ValueError("frame has insufficient contrast")
    return quality
