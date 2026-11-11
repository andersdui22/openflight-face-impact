"""Gate 20/22: extract a candidate silhouette from a selected capture frame.

The returned contour is derived from the actual selected frame image, rather
than an independent caller-supplied contour with unverifiable frame identity.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .ball_contour_extraction import extract_single_bright_contour
from .capture_frame_quality import validate_capture_frame_image
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class CapturedBallContour:
    """Image-derived contour with the capture identity and selected frame index."""

    shot_id: str
    session_id: str
    frame_index: int
    contour_px: np.ndarray

    def __post_init__(self):
        contour = np.array(self.contour_px, dtype=np.float64, copy=True)
        contour.setflags(write=False)
        object.__setattr__(self, "contour_px", contour)


def extract_capture_ball_contour(
    capture: TriggeredCapture,
    frame_index: int,
    *,
    image_size: tuple[int, int],
    threshold: int,
    min_area_px: float,
    border_margin_px: float,
    min_circularity: float = 0.0,
) -> CapturedBallContour:
    """Extract one bright candidate from a verified selected grayscale frame."""
    image = validate_capture_frame_image(capture, frame_index, image_size=image_size)
    contour = extract_single_bright_contour(
        image,
        threshold=threshold,
        min_area_px=min_area_px,
        border_margin_px=border_margin_px,
        min_circularity=min_circularity,
    )
    return CapturedBallContour(
        capture.shot_id, capture.session_id, frame_index, contour,
    )
