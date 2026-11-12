"""Experimental bright fiducial extraction for controlled offline face images.

This detects isolated bright markers, not a clubface or physical impact.
Detected image points are deliberately UNLABELLED; correspondence with known
clubface landmarks must be established separately before any pose estimation.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2 as cv
import numpy as np


@dataclass(frozen=True)
class UnlabelledFaceMarkers:
    """Observed marker centres in pixel coordinates, without face identities."""

    centres_px: np.ndarray
    image_shape: tuple[int, int]

    def __post_init__(self):
        centres = np.asarray(self.centres_px, dtype=np.float64)
        if centres.ndim != 2 or centres.shape[1] != 2 or not np.all(np.isfinite(centres)):
            raise ValueError("marker centres must be finite Nx2")
        centres = np.array(centres, copy=True)
        centres.setflags(write=False)
        object.__setattr__(self, "centres_px", centres)


def extract_unlabelled_bright_markers(
    image: np.ndarray, *, threshold: int = 220,
    min_area_px: float = 5.0, max_area_px: float = 400.0,
    min_circularity: float = 0.6, expected_count: int = 4,
) -> UnlabelledFaceMarkers:
    """Reject ambiguous blobs instead of guessing their face identities.

    For controlled, synthetic or fiducial-marked images only. Not suitable
    for arbitrary unmarked clubheads, reflective balls or real-time capture.
    """
    if not isinstance(image, np.ndarray) or image.ndim != 2 or image.dtype != np.uint8:
        raise ValueError("marker image must be grayscale uint8")
    if not image.size or min(image.shape) < 8:
        raise ValueError("marker image is too small")
    if (not isinstance(threshold, int) or isinstance(threshold, bool)
            or not 0 <= threshold <= 255):
        raise ValueError("threshold must be uint8")
    if not (np.isfinite(min_area_px) and np.isfinite(max_area_px)
            and 0 < min_area_px <= max_area_px):
        raise ValueError("marker area bounds invalid")
    if not np.isfinite(min_circularity) or not 0 < min_circularity <= 1:
        raise ValueError("marker circularity threshold invalid")
    if (not isinstance(expected_count, int) or isinstance(expected_count, bool)
            or not 3 <= expected_count <= 32):
        raise ValueError("expected marker count must be 3..32")
    _, binary = cv.threshold(image, threshold, 255, cv.THRESH_BINARY)
    contours, _ = cv.findContours(binary, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    centres = []
    height, width = image.shape
    for contour in contours:
        area = cv.contourArea(contour)
        if not min_area_px <= area <= max_area_px:
            continue
        perimeter = cv.arcLength(contour, True)
        if perimeter <= 0 or 4 * np.pi * area / perimeter**2 < min_circularity:
            continue
        x, y, w, h = cv.boundingRect(contour)
        if x <= 0 or y <= 0 or x + w >= width or y + h >= height:
            continue
        moments = cv.moments(contour)
        if moments["m00"] <= 0:
            continue
        centres.append((moments["m10"] / moments["m00"],
                        moments["m01"] / moments["m00"]))
    if len(centres) != expected_count:
        raise ValueError("marker observation ambiguous: unexpected blob count")
    points = np.asarray(sorted(centres, key=lambda p: (p[1], p[0])), dtype=np.float64)
    return UnlabelledFaceMarkers(points, image.shape)


def associate_markers_with_reference(
    observation: UnlabelledFaceMarkers,
    reference_pixels_px: np.ndarray,
    *,
    max_distance_px: float,
    min_assignment_margin_px: float = 2.0,
) -> np.ndarray:
    """Associate observed centres with trusted reference pixels, fail closed.

    Reference coordinates must come from a separately established, labelled
    calibration/previous observation, not a guessed spatial ordering. No
    unmarked clubface recognition or physical validation is implied.
    """
    from itertools import permutations

    if not isinstance(observation, UnlabelledFaceMarkers):
        raise ValueError("marker association requires typed observation")
    reference = np.asarray(reference_pixels_px)
    observed = observation.centres_px
    if (reference.ndim != 2 or reference.shape != observed.shape
            or reference.dtype.kind not in "iuf"
            or not np.all(np.isfinite(reference))):
        raise ValueError("reference pixels must be finite and match observed markers")
    if (not np.isfinite(max_distance_px) or max_distance_px <= 0
            or not np.isfinite(min_assignment_margin_px)
            or min_assignment_margin_px < 0):
        raise ValueError("marker association tolerances invalid")
    if len(observed) > 8:
        raise ValueError("exhaustive marker association limited to eight points")
    if len(observed) < 3:
        raise ValueError("marker association needs at least three points")
    costs = np.linalg.norm(reference[:, None, :] - observed[None, :, :], axis=2)
    ranked = []
    for assignment in permutations(range(len(observed))):
        distances = costs[np.arange(len(observed)), assignment]
        ranked.append((float(np.sum(distances ** 2)), assignment, float(np.max(distances))))
    ranked.sort(key=lambda entry: entry[0])
    best, runner_up = ranked[0], ranked[1]
    if best[2] > max_distance_px:
        raise ValueError("marker association exceeds reference distance budget")
    if runner_up[0] - best[0] <= min_assignment_margin_px ** 2:
        raise ValueError("marker association ambiguous")
    matched = np.array(observed[list(best[1])], dtype=np.float64, copy=True)
    matched.setflags(write=False)
    return matched
