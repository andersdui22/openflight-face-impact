"""Offline integration of bright contour extraction and calibrated sphere solver."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.ball_contour_position import estimate_bright_ball_position
from openflight.camera.checkerboard_calibration import CheckerboardCalibration


def calibration():
    return CheckerboardCalibration(
        (320, 240),
        np.array([[260., 0., 160.], [0., 260., 120.], [0., 0., 1.]]),
        np.zeros(5), 0., (),
    )


def disk_image():
    image = np.zeros((240, 320), dtype=np.uint8)
    cv.circle(image, (160, 120), 20, 220, thickness=-1)
    return image


def estimate(image, **overrides):
    options = dict(
        threshold=100, min_area_px=100., border_margin_px=2.,
        ball_radius_mm=21.35, max_ball_residual_rad=0.02,
    )
    options.update(overrides)
    return estimate_bright_ball_position(calibration(), image, **options)


def test_synthetic_disk_produces_finite_forward_candidate():
    result = estimate(disk_image())
    assert result.center_camera_mm.shape == (3,)
    assert np.all(np.isfinite(result.center_camera_mm))
    assert result.center_camera_mm[2] > 0
    assert result.range_mm > 0


def test_rejects_mismatched_calibrated_image_dimensions():
    with pytest.raises(ValueError, match="dimensions"):
        estimate(np.zeros((120, 160), dtype=np.uint8))


def test_rejects_ambiguous_bright_components_before_sphere_fit():
    image = disk_image()
    cv.circle(image, (50, 50), 15, 220, thickness=-1)
    with pytest.raises(ValueError, match="exactly one"):
        estimate(image)


def test_rejects_invalid_radius():
    with pytest.raises(ValueError):
        estimate(disk_image(), ball_radius_mm=-1.)
