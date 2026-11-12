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


def test_synthetic_disk_recovers_known_position_within_one_raster_pixel():
    result = estimate(disk_image())
    assert result.center_camera_mm.shape == (3,)
    assert np.all(np.isfinite(result.center_camera_mm))
    assert result.center_camera_mm[2] > 0
    assert result.range_mm > 0
    # The apparent tangent rim obeys z = R sqrt(1 + (f / r)^2).
    # A one-pixel rim error bounds the depth recovered from the rasterized disk.
    expected_depth = 21.35 * np.sqrt(1 + (260 / 20) ** 2)
    depth_budget = 21.35 * np.sqrt(1 + (260 / 19) ** 2) - expected_depth
    np.testing.assert_allclose(result.center_camera_mm[:2], [0, 0], atol=expected_depth / 260)
    assert result.center_camera_mm[2] == pytest.approx(expected_depth, abs=depth_budget)


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


def test_offset_disk_on_seeded_noisy_gradient_recovers_lateral_position():
    rng = np.random.default_rng(2026)
    background = np.linspace(20, 75, 320) + rng.normal(0, 4, (240, 320))
    image = background.clip(0, 95).astype(np.uint8)
    cv.circle(image, (180, 108), 20, 220, thickness=-1)
    image[14, 20] = image[205, 275] = 255

    result = estimate(image)
    pixel_position = result.center_camera_mm[:2] * 260 / result.center_camera_mm[2] + [160, 120]
    np.testing.assert_allclose(pixel_position, [180, 108], atol=1)


def test_partial_contour_with_nearby_glare_has_no_ball_position():
    image = np.zeros((240, 320), dtype=np.uint8)
    cv.circle(image, (3, 120), 20, 220, thickness=-1)
    cv.circle(image, (200, 80), 3, 255, thickness=-1)
    with pytest.raises(ValueError, match="border|exactly one"):
        estimate(image)
