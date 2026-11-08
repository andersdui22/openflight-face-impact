"""Hardware-free IR-style fixture tests for OpenFlight's existing ball detector.

Synthetic pixel intensities are NOT sensor measurements at 850 nm.
"""

import cv2
import numpy as np
import pytest

from openflight.camera.capture import CapturedFrame
from openflight.camera.detector import BallDetector, DetectorConfig


def _frame(brightness=255, background=0, center=(80, 64), radius=14):
    pixels = np.full((128, 160), background, dtype=np.uint8)
    cv2.circle(pixels, center, radius, int(brightness), -1)
    return CapturedFrame(data=pixels, timestamp=1.5, frame_number=7)


def _detector():
    return BallDetector(DetectorConfig(brightness_threshold=160, min_radius=8, max_radius=25))


def test_existing_detector_finds_bright_synthetic_ball():
    found = _detector().detect(_frame())
    assert found is not None
    assert abs(found.x - 80) <= 3
    assert abs(found.y - 64) <= 3
    assert 8 <= found.radius <= 25
    assert found.frame_number == 7
    assert found.timestamp == 1.5


def test_existing_detector_rejects_ball_below_threshold():
    assert _detector().detect(_frame(brightness=90)) is None


def test_existing_detector_rejects_uniform_dark_frame():
    frame = CapturedFrame(np.zeros((128, 160), dtype=np.uint8), 1.5, 7)
    assert _detector().detect(frame) is None


@pytest.mark.parametrize("center", [(45, 35), (115, 90)])
def test_existing_detector_varied_synthetic_positions(center):
    found = _detector().detect(_frame(center=center))
    assert found is not None
    assert abs(found.x - center[0]) <= 3
    assert abs(found.y - center[1]) <= 3
