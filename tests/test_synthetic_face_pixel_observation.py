"""Image provenance and strict synthetic face-corner extraction."""

from dataclasses import replace

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.synthetic_face_pixel_observation import (
    SyntheticFacePixelObservation, extract_synthetic_face_corners,
)
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def capture_with(image):
    return TriggeredCapture(
        (CameraFrame(image, 100, 1000, 100, 1.0),),
        0, 1000, shot_id="shot", session_id="session",
    )


def fixture():
    image = np.zeros((120, 160), dtype=np.uint8)
    cv.rectangle(image, (35, 25), (75, 65), 220, -1)
    return image


def test_corners_come_from_selected_frame_not_external_pixels():
    result = extract_synthetic_face_corners(
        capture_with(fixture()), 0, image_size=(160, 120),
    )
    assert result.shot_id == "shot" and result.session_id == "session"
    assert result.frame_index == 0
    np.testing.assert_array_equal(
        result.pixels_px, [[35, 65], [75, 65], [75, 25], [35, 25]],
    )
    assert result.pixels_px.flags.writeable is False


def test_observation_defensively_copies_pixels():
    pixels = np.array([[1., 2.], [3., 4.], [5., 6.], [7., 8.]])
    result = SyntheticFacePixelObservation("shot", "session", 0, pixels)
    pixels[:] = 999
    assert result.pixels_px[0, 0] == 1


def test_missing_and_ambiguous_rectangles_fail_closed():
    blank = np.zeros((120, 160), dtype=np.uint8)
    with pytest.raises(ValueError, match="exactly one"):
        extract_synthetic_face_corners(capture_with(blank), 0, image_size=(160, 120))
    image = fixture()
    cv.rectangle(image, (95, 30), (125, 70), 220, -1)
    with pytest.raises(ValueError, match="exactly one"):
        extract_synthetic_face_corners(capture_with(image), 0, image_size=(160, 120))


def test_wrong_frame_and_calibration_rejected():
    with pytest.raises(ValueError, match="frame index"):
        extract_synthetic_face_corners(capture_with(fixture()), 2, image_size=(160, 120))
    with pytest.raises(ValueError, match="dimensions"):
        extract_synthetic_face_corners(capture_with(fixture()), 0, image_size=(120, 160))


def test_invalid_observation_contract_rejected():
    valid = SyntheticFacePixelObservation(
        "shot", "session", 0, np.zeros((4, 2)),
    )
    with pytest.raises(ValueError, match="identity"):
        replace(valid, shot_id=" ")
    with pytest.raises(ValueError, match="frame index"):
        replace(valid, frame_index=True)
    with pytest.raises(ValueError, match="four finite"):
        replace(valid, pixels_px=np.full((4, 2), np.nan))
