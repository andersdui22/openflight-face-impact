"""Offline image-domain checks for an explicitly selected capture frame.

No camera acquisition, feature detection, or physical impact inference occurs.
"""

from __future__ import annotations

import numpy as np

from .trigger_timing_quality import validate_candidate_frame_index
from .triggered_buffer import TriggeredCapture


def validate_capture_frame_image(
    capture: TriggeredCapture,
    frame_index: int,
    *,
    image_size: tuple[int, int],
) -> np.ndarray:
    """Return an independent grayscale image with matching calibrated dimensions.

    Valid capture timing and dimensions do not establish that supplied ball or
    face observations were extracted from this frame.
    """
    index = validate_candidate_frame_index(capture, frame_index)
    if (
        not isinstance(image_size, tuple)
        or len(image_size) != 2
        or any(not isinstance(value, int) or isinstance(value, bool) or value <= 0
               for value in image_size)
    ):
        raise ValueError("image size must be positive integer width and height")
    image = np.asarray(capture.frames[index].image)
    if (
        image.ndim != 2
        or image.dtype != np.uint8
        or image.shape != (image_size[1], image_size[0])
    ):
        raise ValueError("capture frame image must match calibrated grayscale dimensions")
    return np.array(image, copy=True)
