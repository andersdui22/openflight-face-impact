"""Gate 20/21: strict two-object observation in controlled synthetic frames.

This is shape-based fixture recognition, not real ball/club identification.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2 as cv
import numpy as np

from .capture_frame_quality import validate_capture_frame_image
from .synthetic_face_pixel_observation import SyntheticFacePixelObservation
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class SyntheticDualObjectObservation:
    """Two independently copied observations from the same source frame."""

    face: SyntheticFacePixelObservation
    ball_contour_px: np.ndarray
    physical_objects_confirmed: bool = False

    def __post_init__(self) -> None:
        if self.physical_objects_confirmed is not False:
            raise ValueError("synthetic shapes do not confirm physical objects")
        contour = np.asarray(self.ball_contour_px)
        if (contour.ndim != 2 or contour.shape[1] != 2
                or len(contour) < 8 or not np.all(np.isfinite(contour))):
            raise ValueError("invalid synthetic ball contour")
        copied = np.array(contour, dtype=np.float64, copy=True)
        copied.setflags(write=False)
        object.__setattr__(self, "ball_contour_px", copied)


def extract_synthetic_ball_and_face(
    capture: TriggeredCapture,
    frame_index: int,
    *,
    image_size: tuple[int, int],
    threshold: int = 180,
    min_area_px: float = 100.,
    border_margin_px: int = 2,
    min_ball_circularity: float = 0.85,
) -> SyntheticDualObjectObservation:
    """Require exactly one circular and one quadrilateral bright component.

    No heuristic selection among competing objects; all ambiguity is rejected.
    """
    if type(threshold) is not int or not 1 <= threshold <= 255:
        raise ValueError("invalid threshold")
    if (not np.isfinite(min_area_px) or min_area_px <= 0
            or not np.isfinite(min_ball_circularity)
            or not 0 < min_ball_circularity <= 1
            or type(border_margin_px) is not int or border_margin_px < 0):
        raise ValueError("invalid shape thresholds")
    image = validate_capture_frame_image(capture, frame_index, image_size=image_size)
    mask = (image >= threshold).astype(np.uint8) * 255
    contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    if len(contours) != 2:
        raise ValueError("expected exactly two isolated synthetic objects")
    faces = []
    balls = []
    width, height = image_size
    for contour in contours:
        area = float(cv.contourArea(contour))
        perimeter = float(cv.arcLength(contour, True))
        if area < min_area_px or perimeter <= 0:
            raise ValueError("synthetic object below minimum area")
        points = contour.reshape(-1, 2)
        if (np.any(points[:, 0] < border_margin_px)
                or np.any(points[:, 0] >= width - border_margin_px)
                or np.any(points[:, 1] < border_margin_px)
                or np.any(points[:, 1] >= height - border_margin_px)):
            raise ValueError("synthetic object touches excluded border")
        component = np.zeros_like(mask)
        cv.drawContours(component, [contour], -1, 255, cv.FILLED)
        if cv.countNonZero(cv.bitwise_and(component, cv.bitwise_not(mask))):
            raise ValueError("synthetic object contains an interior hole")
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        approx = cv.approxPolyDP(contour, 0.015 * perimeter, True)
        if circularity >= min_ball_circularity and len(approx) > 4:
            balls.append(points)
        elif len(approx) == 4 and cv.isContourConvex(approx):
            corners = approx.reshape(4, 2).astype(np.float64)
            order = np.argsort(corners[:, 1], kind="stable")
            top, bottom = corners[order[:2]], corners[order[2:]]
            if (np.max(top[:, 1]) >= np.min(bottom[:, 1])
                    or top[0, 0] == top[1, 0]
                    or bottom[0, 0] == bottom[1, 0]):
                raise ValueError("ambiguous synthetic face corner ordering")
            top = top[np.argsort(top[:, 0])]
            bottom = bottom[np.argsort(bottom[:, 0])]
            faces.append(np.stack((bottom[0], bottom[1], top[1], top[0])))
        else:
            raise ValueError("unrecognized synthetic object geometry")
    if len(faces) != 1 or len(balls) != 1:
        raise ValueError("ambiguous synthetic ball and face identities")
    return SyntheticDualObjectObservation(
        SyntheticFacePixelObservation(
            capture.shot_id, capture.session_id, frame_index, faces[0],
        ),
        balls[0],
    )
