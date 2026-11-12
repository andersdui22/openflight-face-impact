"""Image-derived labelled corners for a controlled synthetic face fixture.

Reuse Gate 10's strict rectangular candidate proposal. This is NOT a
general clubface detector and cannot establish real-world landmark identity.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .capture_frame_quality import validate_capture_frame_image
from .synthetic_face_proposal import propose_synthetic_ir_face_region
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class SyntheticFacePixelObservation:
    """Copied image-derived pixels with explicit capture provenance."""

    shot_id: str
    session_id: str
    frame_index: int
    pixels_px: np.ndarray

    def __post_init__(self) -> None:
        if (not isinstance(self.shot_id, str) or not self.shot_id.strip()
                or not isinstance(self.session_id, str) or not self.session_id.strip()):
            raise ValueError("observation requires capture identity")
        if (not isinstance(self.frame_index, int) or isinstance(self.frame_index, bool)
                or self.frame_index < 0):
            raise ValueError("observation requires nonnegative frame index")
        pixels = np.asarray(self.pixels_px)
        if (pixels.shape != (4, 2) or pixels.dtype.kind not in "iuf"
                or not np.all(np.isfinite(pixels))):
            raise ValueError("observation requires four finite labelled pixels")
        copied = np.array(pixels, dtype=np.float64, copy=True)
        copied.setflags(write=False)
        object.__setattr__(self, "pixels_px", copied)


def extract_synthetic_face_corners(
    capture: TriggeredCapture,
    frame_index: int,
    *,
    image_size: tuple[int, int],
    threshold: int = 180,
) -> SyntheticFacePixelObservation:
    """Derive ordered corners from the *selected* frame's bright rectangle.

    Pixel order: bottom-left, bottom-right, top-right, top-left, matching
    face-local heel/bottom, toe/bottom, toe/top, heel/top conventions.
    This order is an explicitly synthetic fixture convention, not evidence
    of real club handedness or physical face orientation.
    """
    image = validate_capture_frame_image(capture, frame_index, image_size=image_size)
    region = propose_synthetic_ir_face_region(image, threshold=threshold)
    left, top, right, bottom = region.bounds
    pixels = np.array(
        [[left, bottom], [right, bottom], [right, top], [left, top]],
        dtype=np.float64,
    )
    return SyntheticFacePixelObservation(
        shot_id=capture.shot_id,
        session_id=capture.session_id,
        frame_index=frame_index,
        pixels_px=pixels,
    )
