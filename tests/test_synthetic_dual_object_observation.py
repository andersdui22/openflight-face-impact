"""Strict dual-object synthetic frame observations and ambiguity rejection."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.synthetic_dual_object_observation import (
    extract_synthetic_ball_and_face,
)
from openflight.camera.triggered_buffer import CameraFrame, TriggeredCapture


def capture(image):
    return TriggeredCapture(
        (CameraFrame(image.copy(), 100, 1000, 100, 1.),
         CameraFrame(image.copy(), 200, 2000, 100, 1.)),
        1, 1500, shot_id="shot", session_id="session",
    )


def scene():
    image = np.zeros((240, 320), dtype=np.uint8)
    cv.rectangle(image, (35, 40), (115, 95), 230, -1)
    cv.circle(image, (240, 150), 20, 220, -1)
    return image


def observe(image):
    return extract_synthetic_ball_and_face(
        capture(image), 1, image_size=(320, 240),
    )


def test_two_distinct_objects_have_one_shared_capture_identity():
    result = observe(scene())
    assert result.face.frame_index == 1
    assert result.face.shot_id == "shot"
    assert result.face.session_id == "session"
    assert result.face.pixels_px.shape == (4, 2)
    assert len(result.ball_contour_px) >= 8
    assert result.ball_contour_px.flags.writeable is False
    assert result.physical_objects_confirmed is False


def test_blank_and_ball_only_are_rejected():
    blank = np.zeros((240, 320), dtype=np.uint8)
    with pytest.raises(ValueError, match="exactly two"):
        observe(blank)
    cv.circle(blank, (160, 120), 20, 220, -1)
    with pytest.raises(ValueError, match="exactly two"):
        observe(blank)


def test_extra_object_and_occluded_ball_are_rejected():
    extra = scene()
    cv.circle(extra, (160, 200), 15, 220, -1)
    with pytest.raises(ValueError, match="exactly two"):
        observe(extra)
    occluded = scene()
    cv.circle(occluded, (240, 150), 8, 0, -1)
    with pytest.raises(ValueError, match="interior hole"):
        observe(occluded)


def test_two_circles_cannot_be_misidentified_as_face():
    image = np.zeros((240, 320), dtype=np.uint8)
    cv.circle(image, (90, 90), 25, 220, -1)
    cv.circle(image, (240, 150), 20, 220, -1)
    with pytest.raises(ValueError, match="ambiguous"):
        observe(image)


def test_low_level_noise_does_not_change_observations():
    clean = scene()
    noise = np.random.default_rng(12).integers(
        0, 50, clean.shape, dtype=np.uint8,
    )
    noisy = np.maximum(clean, noise)
    a, b = observe(clean), observe(noisy)
    np.testing.assert_array_equal(a.face.pixels_px, b.face.pixels_px)
    np.testing.assert_array_equal(a.ball_contour_px, b.ball_contour_px)
