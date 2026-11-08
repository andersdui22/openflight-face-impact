"""Locate explicitly color-coded objects in controlled synthetic RGB frames.

This is an annotation-fixture validator, NOT a real-world ball/face detector.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

BALL_COLOR = (255, 0, 0)
FACE_COLOR = (0, 255, 0)


@dataclass(frozen=True)
class SyntheticObjectLocation:
    """Image center (column, row) and inclusive bounding box in pixels."""

    center: tuple[float, float]
    bounds: tuple[int, int, int, int]  # left, top, right, bottom


def _marker_bounds(image: np.ndarray, color: tuple[int, int, int]):
    mask = np.all(image == color, axis=2)
    rows, columns = np.nonzero(mask)
    if len(rows) == 0:
        raise ValueError("Required synthetic object marker is missing")
    left, right = int(columns.min()), int(columns.max())
    top, bottom = int(rows.min()), int(rows.max())
    return mask, left, top, right, bottom


def locate_synthetic_ball_and_face(
    frame: np.ndarray,
) -> tuple[SyntheticObjectLocation, SyntheticObjectLocation]:
    """Locate one red disk and one green filled rectangle in an RGB fixture.

    Synthetic marker colors must match exactly. This deliberately rejects
    natural images, imperfect shapes, partial objects and ambiguous markers.
    """
    image = np.asarray(frame)
    if image.ndim != 3 or image.shape[2] != 3 or image.shape[0] == 0 or image.shape[1] == 0:
        raise ValueError("Expected a nonempty HxWx3 synthetic RGB frame")
    if image.dtype != np.uint8:
        raise ValueError("Expected uint8 synthetic RGB markers")

    ball_mask, left, top, right, bottom = _marker_bounds(image, BALL_COLOR)
    diameter_x, diameter_y = right - left + 1, bottom - top + 1
    if diameter_x != diameter_y or diameter_x < 5 or diameter_x % 2 != 1:
        raise ValueError("Synthetic ball marker must be an odd-diameter disk")
    radius = diameter_x // 2
    center_x, center_y = left + radius, top + radius
    yy, xx = np.ogrid[: image.shape[0], : image.shape[1]]
    expected_ball = (xx - center_x) ** 2 + (yy - center_y) ** 2 <= radius**2
    if not np.array_equal(ball_mask, expected_ball):
        raise ValueError("Synthetic ball marker is incomplete or ambiguous")
    ball = SyntheticObjectLocation((float(center_x), float(center_y)), (left, top, right, bottom))

    face_mask, left, top, right, bottom = _marker_bounds(image, FACE_COLOR)
    if right - left < 2 or bottom - top < 2:
        raise ValueError("Synthetic clubface marker is too small")
    expected_face = np.zeros(face_mask.shape, dtype=bool)
    expected_face[top : bottom + 1, left : right + 1] = True
    if not np.array_equal(face_mask, expected_face):
        raise ValueError("Synthetic clubface marker is incomplete or ambiguous")
    face = SyntheticObjectLocation(((left + right) / 2, (top + bottom) / 2), (left, top, right, bottom))
    return ball, face
