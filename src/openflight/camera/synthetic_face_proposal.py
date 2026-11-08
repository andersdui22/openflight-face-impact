"""Fixture-only proposal of an isolated bright rectangular face candidate.

A bright rectangle is not proof of a real golf clubface. This helper only
removes the manually supplied crop from controlled synthetic fixtures.
"""

import cv2
import numpy as np

from .synthetic_ir_face import SyntheticFaceRegion, locate_synthetic_ir_face


def propose_synthetic_ir_face_region(
    frame: np.ndarray, threshold: int = 180
) -> SyntheticFaceRegion:
    """Return one isolated filled rectangle, ignoring nonrectangular blobs.

    All bounds and centers are full-frame image pixels. Multiple rectangles,
    touching/partial shapes and invalid fixtures fail closed.
    """
    image = np.asarray(frame)
    if image.ndim != 2 or image.dtype != np.uint8 or not image.size:
        raise ValueError("Expected nonempty uint8 grayscale synthetic frame")
    if type(threshold) is not int or not 1 <= threshold <= 255:
        raise ValueError("Threshold must be an integer between 1 and 255")

    mask = (image >= threshold).astype(np.uint8)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    candidates = []
    for index in range(1, count):
        left, top, width, height, area = (int(v) for v in stats[index])
        if width < 3 or height < 3 or area != width * height:
            continue
        right, bottom = left + width - 1, top + height - 1
        if left == 0 or top == 0 or right == image.shape[1] - 1 or bottom == image.shape[0] - 1:
            raise ValueError("Synthetic rectangular candidate touches frame edge")
        # Reuse Gate 08's strict rectangle detector, not an independent
        # geometry/clubface implementation.
        isolated = np.where(labels[top : bottom + 1, left : right + 1] == index, 255, 0).astype(np.uint8)
        local = locate_synthetic_ir_face(isolated, threshold=threshold)
        candidates.append(
            SyntheticFaceRegion(
                bounds=(left, top, right, bottom),
                center=(left + local.center[0], top + local.center[1]),
            )
        )
    if len(candidates) != 1:
        raise ValueError("Expected exactly one synthetic rectangular face candidate")
    return candidates[0]
