"""Gate 22 offline capture image-domain provenance checks."""

from dataclasses import replace

import numpy as np
import pytest

from openflight.camera.capture_frame_quality import validate_capture_frame_image
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def capture_with_image(image):
    frames = tuple(
        CameraFrame(np.full((4, 6), i, dtype=np.uint8), i * 100, i * 1000, 100, 1.)
        for i in (1, 2)
    ) + (CameraFrame(image, 300, 3000, 100, 1.),)
    return TriggeredCapture(
        frames, 2, 2500, shot_id="shot-1", session_id="session-1",
    )


def test_valid_selected_image_is_copied_and_not_aliased():
    image = np.full((4, 6), 9, dtype=np.uint8)
    capture = capture_with_image(image)
    result = validate_capture_frame_image(capture, 2, image_size=(6, 4))
    np.testing.assert_array_equal(result, image)
    image[0, 0] = 55
    assert result[0, 0] == 9


@pytest.mark.parametrize("image", [
    np.zeros((4, 5), dtype=np.uint8),
    np.zeros((6, 4), dtype=np.uint8),
    np.zeros((4, 6, 1), dtype=np.uint8),
    np.zeros((4, 6), dtype=np.uint16),
    np.zeros((4, 6), dtype=float),
])
def test_rejects_mismatched_image_domain(image):
    with pytest.raises(ValueError, match="grayscale dimensions"):
        validate_capture_frame_image(capture_with_image(image), 2, image_size=(6, 4))


@pytest.mark.parametrize("size", [(0, 4), (6, True), (6, 4, 1), [6, 4]])
def test_rejects_invalid_declared_size(size):
    with pytest.raises(ValueError, match="image size"):
        validate_capture_frame_image(
            capture_with_image(np.zeros((4, 6), dtype=np.uint8)), 2, image_size=size,
        )


def test_rejects_invalid_capture_and_frame_index():
    capture = capture_with_image(np.zeros((4, 6), dtype=np.uint8))
    with pytest.raises(ValueError, match="candidate frame index"):
        validate_capture_frame_image(capture, 3, image_size=(6, 4))
    with pytest.raises(ValueError, match="capture identity"):
        validate_capture_frame_image(
            replace(capture, session_id=""), 2, image_size=(6, 4),
        )
