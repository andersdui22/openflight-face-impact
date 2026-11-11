"""Offline synthetic perspective quadrilateral evidence and rejections."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.synthetic_face_quadrilateral import extract_synthetic_quadrilateral_corners
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def capture(image):
    return TriggeredCapture(
        (CameraFrame(image.copy(), 100, 1000, 100, 1.0),
         CameraFrame(image.copy(), 200, 2000, 100, 1.0)),
        1, 1500, shot_id="shot", session_id="session",
    )


def polygon_image(points):
    image = np.zeros((160, 240), dtype=np.uint8)
    cv.fillConvexPoly(image, np.array(points, dtype=np.int32), 230)
    return image


def observe(image, **kwargs):
    return extract_synthetic_quadrilateral_corners(
        capture(image), 1, image_size=(240, 160), **kwargs,
    )


def test_perspective_fixture_produces_provenanced_corners():
    image = polygon_image([[60, 40], [151, 51], [139, 109], [51, 102]])
    result = observe(image)
    assert result.shot_id == "shot"
    assert result.session_id == "session"
    assert result.frame_index == 1
    assert result.pixels_px.shape == (4, 2)
    assert result.pixels_px.flags.writeable is False
    assert result.pixels_px[0, 1] > result.pixels_px[3, 1]


def test_blank_and_multiple_shapes_fail_closed():
    with pytest.raises(ValueError, match="exactly one"):
        observe(np.zeros((160, 240), dtype=np.uint8))
    image = polygon_image([[60, 40], [150, 40], [150, 100], [60, 100]])
    cv.rectangle(image, (180, 30), (215, 65), 230, -1)
    with pytest.raises(ValueError, match="exactly one"):
        observe(image)


def test_nonquadrilateral_rejected():
    image = np.zeros((160, 240), dtype=np.uint8)
    cv.circle(image, (110, 80), 35, 230, -1)
    with pytest.raises(ValueError, match="convex quadrilateral"):
        observe(image)


def test_border_and_wrong_frame_rejected():
    image = polygon_image([[0, 30], [100, 30], [100, 100], [0, 100]])
    with pytest.raises(ValueError, match="border"):
        observe(image)
    with pytest.raises(ValueError, match="frame index"):
        extract_synthetic_quadrilateral_corners(
            capture(image), 3, image_size=(240, 160),
        )


@pytest.mark.parametrize("threshold", [0, 256, True, 100.5])
def test_invalid_threshold_rejected(threshold):
    with pytest.raises(ValueError, match="threshold"):
        observe(polygon_image([[50, 40], [150, 40], [150, 100], [50, 100]]),
                threshold=threshold)
