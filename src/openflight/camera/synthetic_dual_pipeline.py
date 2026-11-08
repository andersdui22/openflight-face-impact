"""Fixture-only composition of existing ball and face detectors.

The face crop is explicitly supplied by a synthetic test. No real clubface
recognition, physical impact location or calibrated units are inferred.
"""

from dataclasses import dataclass

import numpy as np

from .capture import CapturedFrame
from .detector import BallDetector, DetectedBall
from .synthetic_ir_face import SyntheticFaceRegion, locate_synthetic_ir_face


@dataclass(frozen=True)
class SyntheticDualDetection:
    """Full-frame pixel detections and original frame metadata."""

    ball: DetectedBall
    face: SyntheticFaceRegion
    frame_number: int
    timestamp: float


def locate_synthetic_ball_and_ir_face(
    frame: CapturedFrame,
    face_crop_bounds: tuple[int, int, int, int],
    *,
    detector: BallDetector,
    face_threshold: int = 180,
) -> SyntheticDualDetection:
    """Reuse both detectors with a caller-annotated inclusive face-only crop.

    The crop bounds are (left, top, right, bottom) in full-frame pixels.
    A valid synthetic result is not proof of clubface identity or impact.
    """
    image = np.asarray(frame.data)
    if image.ndim != 2 or image.dtype != np.uint8 or not image.size:
        raise ValueError("Expected nonempty uint8 grayscale synthetic frame")
    if (
        not isinstance(face_crop_bounds, tuple)
        or len(face_crop_bounds) != 4
        or any(type(v) is not int for v in face_crop_bounds)
    ):
        raise ValueError("Expected four integer inclusive crop bounds")
    left, top, right, bottom = face_crop_bounds
    height, width = image.shape
    if not (0 <= left <= right < width and 0 <= top <= bottom < height):
        raise ValueError("Face crop is outside synthetic frame")

    # Preserve the existing ball detector; do not modify its public API.
    ball = detector.detect(frame)
    if ball is None:
        raise ValueError("No synthetic ball detected")
    face_local = locate_synthetic_ir_face(
        image[top : bottom + 1, left : right + 1], threshold=face_threshold
    )
    x0, y0, x1, y1 = face_local.bounds
    face = SyntheticFaceRegion(
        bounds=(left + x0, top + y0, left + x1, top + y1),
        center=(left + face_local.center[0], top + face_local.center[1]),
    )
    # Reject the ball overlapping the annotated face region; this simple
    # synthetic policy avoids treating ambiguous pixels as an impact event.
    closest_x = max(face.bounds[0], min(ball.x, face.bounds[2]))
    closest_y = max(face.bounds[1], min(ball.y, face.bounds[3]))
    if (ball.x - closest_x) ** 2 + (ball.y - closest_y) ** 2 <= ball.radius**2:
        raise ValueError("Synthetic ball overlaps annotated face region")
    return SyntheticDualDetection(ball, face, frame.frame_number, frame.timestamp)
