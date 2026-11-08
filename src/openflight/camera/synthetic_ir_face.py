"""Conservative localization of an isolated synthetic bright face rectangle.

This is a fixture-only region locator, NOT a real clubface pose estimator.
"""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class SyntheticFaceRegion:
    """Inclusive pixel bounds and center (column, row) of a fixture rectangle."""

    bounds: tuple[int, int, int, int]
    center: tuple[float, float]


def locate_synthetic_ir_face(frame: np.ndarray, threshold: int = 180) -> SyntheticFaceRegion:
    """Accept exactly one bright axis-aligned rectangle on a dark fixture.

    Reflections, extra bright objects and partial rectangles fail closed.
    The caller must provide a face-only crop: this does not distinguish a
    real clubface from other rectangular bright objects.
    """
    image = np.asarray(frame)
    if image.ndim != 2 or image.dtype != np.uint8 or not image.size:
        raise ValueError("Expected a nonempty uint8 grayscale synthetic crop")
    if not isinstance(threshold, int) or not 1 <= threshold <= 255:
        raise ValueError("Threshold must be an integer between 1 and 255")
    mask = image >= threshold
    rows, columns = np.nonzero(mask)
    if not len(rows):
        raise ValueError("No bright synthetic face region")
    left, right = int(columns.min()), int(columns.max())
    top, bottom = int(rows.min()), int(rows.max())
    if right - left < 2 or bottom - top < 2:
        raise ValueError("Synthetic face region too small")
    expected = np.zeros(mask.shape, dtype=bool)
    expected[top : bottom + 1, left : right + 1] = True
    if not np.array_equal(mask, expected):
        raise ValueError("Bright pixels do not form exactly one filled rectangle")
    return SyntheticFaceRegion(
        bounds=(left, top, right, bottom),
        center=((left + right) / 2, (top + bottom) / 2),
    )
