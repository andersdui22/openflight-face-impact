"""Strict synthetic perspective quadrilateral observation from capture pixels.

Not a real golf clubface classifier: a single bright quadrilateral can be
another object. Orientation is an explicit image-only fixture convention.
"""

from __future__ import annotations

import cv2 as cv
import numpy as np

from .synthetic_face_pixel_observation import SyntheticFacePixelObservation
from .capture_frame_quality import validate_capture_frame_image
from .triggered_buffer import TriggeredCapture


def extract_synthetic_quadrilateral_corners(
    capture: TriggeredCapture,
    frame_index: int,
    *,
    image_size: tuple[int, int],
    threshold: int = 180,
    min_area_px: float = 100.0,
    min_fill_ratio: float = 0.85,
    border_margin_px: int = 2,
) -> SyntheticFacePixelObservation:
    """Accept exactly one convex, isolated, filled synthetic quadrilateral.

    Ordered output is bottom-left, bottom-right, top-right, top-left based on
    image row/column. This ordering is only valid for upright synthetic
    fixtures, not arbitrary club rotation or handedness.
    """
    if type(threshold) is not int or not 1 <= threshold <= 255:
        raise ValueError("threshold must be an integer from 1 to 255")
    if (not np.isfinite(min_area_px) or min_area_px <= 0
            or not np.isfinite(min_fill_ratio) or not 0 < min_fill_ratio <= 1):
        raise ValueError("invalid quadrilateral acceptance thresholds")
    if type(border_margin_px) is not int or border_margin_px < 0:
        raise ValueError("invalid quadrilateral border margin")
    image = validate_capture_frame_image(capture, frame_index, image_size=image_size)
    mask = (image >= threshold).astype(np.uint8) * 255
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    if len(contours) != 1:
        raise ValueError("expected exactly one isolated synthetic quadrilateral")
    contour = contours[0]
    area = float(cv.contourArea(contour))
    perimeter = float(cv.arcLength(contour, True))
    if area < min_area_px or perimeter <= 0:
        raise ValueError("synthetic quadrilateral is too small")
    approx = cv.approxPolyDP(contour, 0.015 * perimeter, True)
    if len(approx) != 4 or not cv.isContourConvex(approx):
        raise ValueError("synthetic region is not a convex quadrilateral")
    corners = approx.reshape(4, 2).astype(np.float64)
    width, height = image_size
    if (np.any(corners[:, 0] < border_margin_px)
            or np.any(corners[:, 0] >= width - border_margin_px)
            or np.any(corners[:, 1] < border_margin_px)
            or np.any(corners[:, 1] >= height - border_margin_px)):
        raise ValueError("synthetic quadrilateral touches excluded image border")
    polygon_area = abs(float(cv.contourArea(approx)))
    if polygon_area <= 0 or area / polygon_area < min_fill_ratio:
        raise ValueError("synthetic quadrilateral has insufficient fill")
    # Split corners by their y positions; upright synthetic fixtures only.
    order = np.argsort(corners[:, 1], kind="stable")
    top = corners[order[:2]]
    bottom = corners[order[2:]]
    if (np.max(top[:, 1]) >= np.min(bottom[:, 1])
            or top[0, 0] == top[1, 0] or bottom[0, 0] == bottom[1, 0]):
        raise ValueError("synthetic quadrilateral corner order is ambiguous")
    top = top[np.argsort(top[:, 0])]
    bottom = bottom[np.argsort(bottom[:, 0])]
    pixels = np.stack((bottom[0], bottom[1], top[1], top[0]))
    return SyntheticFacePixelObservation(
        capture.shot_id, capture.session_id, frame_index, pixels,
    )
