"""Synthetic end-to-end fixture tests for the two existing detectors."""

import cv2
import numpy as np
import pytest

from openflight.camera.capture import CapturedFrame
from openflight.camera.detector import BallDetector, DetectorConfig
from openflight.camera.synthetic_dual_pipeline import locate_synthetic_ball_and_ir_face


def _frame(ball=True, face=True):
    image = np.zeros((160, 240), dtype=np.uint8)
    if ball:
        cv2.circle(image, (48, 65), 14, 255, -1)
    if face:
        image[80:111, 150:191] = 230
    return CapturedFrame(data=image, timestamp=2.5, frame_number=9)


def _run(frame, crop=(140, 70, 200, 120)):
    detector = BallDetector(DetectorConfig(brightness_threshold=160, min_radius=8, max_radius=25))
    return locate_synthetic_ball_and_ir_face(frame, crop, detector=detector)


def test_both_objects_have_full_frame_pixel_coordinates():
    result = _run(_frame())
    assert abs(result.ball.x - 48) <= 3
    assert abs(result.ball.y - 65) <= 3
    assert result.face.bounds == (150, 80, 190, 110)
    assert result.face.center == (170.0, 95.0)
    assert result.frame_number == 9
    assert result.timestamp == 2.5


def test_missing_ball_fails_closed():
    with pytest.raises(ValueError, match="No synthetic ball"):
        _run(_frame(ball=False))


def test_missing_face_fails_closed():
    with pytest.raises(ValueError, match="No bright synthetic face"):
        _run(_frame(face=False))


def test_unexpected_bright_reflection_in_crop_fails_closed():
    frame = _frame()
    frame.data[75, 145] = 255
    with pytest.raises(ValueError, match="exactly one"):
        _run(frame)


@pytest.mark.parametrize("crop", [(0, 0, 250, 100), (140, 70, 130, 120), (140, 70, 200), (140, 70, True, 120)])
def test_invalid_crop_fails_closed(crop):
    with pytest.raises(ValueError, match="crop"):
        _run(_frame(), crop)


def test_invalid_full_frame_fails_closed():
    bad = CapturedFrame(data=np.zeros((10, 10, 3), dtype=np.uint8), timestamp=0, frame_number=0)
    with pytest.raises(ValueError, match="grayscale"):
        _run(bad)
