"""Offline Gate 20 supplied contour quality tests."""

import numpy as np
import pytest

from openflight.camera.ball_contour_quality import validate_ball_contour_pixels


RIM = np.array([[50., 50.], [60., 40.], [70., 50.],
                [65., 60.], [55., 60.]])


def test_valid_contour_returns_independent_float_copy():
    original = RIM.copy()
    result = validate_ball_contour_pixels(RIM, image_size=(100, 80), border_margin_px=3.)
    RIM[0, 0] = 51.
    try:
        np.testing.assert_array_equal(result, original)
        assert result.dtype == np.float64
    finally:
        RIM[0, 0] = 50.


@pytest.mark.parametrize("bad", [
    RIM[:4], np.vstack((RIM[:4], RIM[0])),
    np.array([[1., 2.]]), np.array([[1., 2., 3.]]),
    np.array([["a", "b"]] * 5),
    np.array([[float("nan"), 10.]] * 5),
])
def test_malformed_contour_fails_closed(bad):
    with pytest.raises(ValueError, match="ball contour"):
        validate_ball_contour_pixels(bad, image_size=(100, 80), border_margin_px=2.)


@pytest.mark.parametrize("bad", [
    np.array([[0., 50.], [60., 40.], [70., 50.], [65., 60.], [55., 60.]]),
    np.array([[50., 50.], [60., 40.], [99., 50.], [65., 60.], [55., 60.]]),
])
def test_border_clipping_rejected(bad):
    with pytest.raises(ValueError, match="border margin"):
        validate_ball_contour_pixels(bad, image_size=(100, 80), border_margin_px=2.)


@pytest.mark.parametrize("size,margin", [
    ((0, 80), 2.), ((100, 80), -1.), ((100, 80), float("nan")),
    ((100, 80), 40.), ((100, 80), True),
])
def test_invalid_image_domain_rejected(size, margin):
    with pytest.raises(ValueError):
        validate_ball_contour_pixels(RIM, image_size=size, border_margin_px=margin)
