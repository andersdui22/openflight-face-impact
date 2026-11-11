"""Controlled raster marker extraction; not real clubface recognition."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.experimental_face_markers import extract_unlabelled_bright_markers


def _image():
    image = np.zeros((240, 320), dtype=np.uint8)
    for x, y in ((40, 45), (250, 50), (45, 190), (245, 185)):
        cv.circle(image, (x, y), 5, 255, -1)
    return image


def test_four_bright_synthetic_fiducials_detected_without_manual_pixel_inputs():
    observed = extract_unlabelled_bright_markers(_image())
    assert observed.image_shape == (240, 320)
    assert observed.centres_px.shape == (4, 2)
    np.testing.assert_allclose(
        observed.centres_px,
        [[40., 45.], [250., 50.], [245., 185.], [45., 190.]],
        atol=0.5,
    )
    assert observed.centres_px.flags.writeable is False


def test_missing_marker_fails_closed():
    image = _image()
    cv.circle(image, (40, 45), 6, 0, -1)
    with pytest.raises(ValueError, match="unexpected blob count"):
        extract_unlabelled_bright_markers(image)


def test_extra_marker_fails_closed():
    image = _image()
    cv.circle(image, (150, 120), 5, 255, -1)
    with pytest.raises(ValueError, match="unexpected blob count"):
        extract_unlabelled_bright_markers(image)


@pytest.mark.parametrize("image", [
    np.zeros((240, 320, 3), dtype=np.uint8),
    np.zeros((240, 320), dtype=np.float32),
    np.zeros((4, 4), dtype=np.uint8),
])
def test_unsupported_images_rejected(image):
    with pytest.raises(ValueError):
        extract_unlabelled_bright_markers(image)
