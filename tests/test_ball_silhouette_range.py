"""Verify the camera-only sphere estimate with known synthetic silhouettes."""

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.ball_silhouette_range import estimate_ball_position
from openflight.camera.calibrated_rays import calibrated_pixel_rays
from openflight.camera.checkerboard_calibration import CheckerboardCalibration

RADIUS = 21.35


def tangent_rim(center, azimuths, radius=RADIUS):
    center = np.asarray(center, dtype=float)
    direction = center / np.linalg.norm(center)
    transverse = np.cross(direction, [0, 1, 0])
    transverse /= np.linalg.norm(transverse)
    tangent = np.cross(direction, transverse)
    # Construct tangent points on the sphere, then observe them from the origin.
    radius_ratio = radius / np.linalg.norm(center)
    ring_center = center - radius * radius_ratio * direction
    ring_radius = radius * np.sqrt(1 - radius_ratio**2)
    ring = ring_center + ring_radius * (
        np.cos(azimuths)[:, None] * transverse + np.sin(azimuths)[:, None] * tangent
    )
    return ring / np.linalg.norm(ring, axis=1, keepdims=True)


@pytest.fixture
def angles():
    return np.array([0, 0.34, 0.93, 1.61, 2.57, 3.02, 3.84, 4.96, 5.71])


@pytest.mark.parametrize("center", [[0, 0, 260], [215, -82, 510], [-300, 140, 1350]])
def test_recovers_known_center_from_calibrated_distorted_pixels(center, angles):
    optics = CheckerboardCalibration(
        (640, 400),
        np.array([[530.0, 0, 315], [0, 525.0, 198], [0, 0, 1]]),
        np.array([-0.24, 0.08, 0.002, -0.003, 0.01]),
        0.0,
        (),
    )
    rim = tangent_rim(center, angles)
    pixels, _ = cv.projectPoints(
        rim, np.zeros(3), np.zeros(3), optics.camera_matrix, optics.distortion
    )
    rays = calibrated_pixel_rays(optics, pixels.reshape(-1, 2), image_size=optics.image_size)
    result = estimate_ball_position(rays, radius_mm=RADIUS, max_residual_rad=1e-6)
    np.testing.assert_allclose(result.center_camera_mm, center, atol=1e-5)
    assert result.range_mm == pytest.approx(np.linalg.norm(center), abs=1e-5)
    assert result.max_residual_rad < 1e-8


def test_small_observation_noise_remains_within_budget(angles):
    center = np.array([120, -60, 600])
    rays = tangent_rim(center, angles)
    rays[:, 0] += np.linspace(-1e-5, 1e-5, len(rays))
    rays /= np.linalg.norm(rays, axis=1, keepdims=True)
    result = estimate_ball_position(rays, radius_mm=RADIUS, max_residual_rad=5e-5)
    np.testing.assert_allclose(result.center_camera_mm, center, atol=0.3)


def test_partial_rim_is_rejected_even_with_perfect_tangency():
    rays = tangent_rim([50, 0, 500], np.linspace(-0.8, 0.8, 8))
    with pytest.raises(ValueError, match="more than half"):
        estimate_ball_position(rays, radius_mm=RADIUS, max_residual_rad=1e-6)


def test_inconsistent_rim_is_rejected(angles):
    rays = tangent_rim([50, 0, 500], angles)
    rays[-1] = tangent_rim([50, 0, 500], angles[-1:], radius=RADIUS * 1.35)[0]
    with pytest.raises(ValueError, match="disagree"):
        estimate_ball_position(rays, radius_mm=RADIUS, max_residual_rad=1e-4)


def test_unresolved_angular_size_is_rejected(angles):
    rays = tangent_rim([0, 0, 2e6], angles)
    with pytest.raises(ValueError, match="too small"):
        estimate_ball_position(rays, radius_mm=RADIUS, max_residual_rad=1e-4)


@pytest.mark.parametrize("radius", [0.0, -1.0, float("nan"), float("inf")])
def test_requires_an_explicit_valid_radius(angles, radius):
    rays = tangent_rim([0, 0, 500], angles)
    with pytest.raises(ValueError, match="radius"):
        estimate_ball_position(rays, radius_mm=radius, max_residual_rad=1e-6)


def test_rejects_too_few_duplicate_and_unnormalized_rays(angles):
    rays = tangent_rim([0, 0, 500], angles)
    for malformed, message in ((rays[:4], "at least five"),
                               (np.vstack((rays, rays[0])), "distinct"),
                               (rays * 2, "unit length")):
        with pytest.raises(ValueError, match=message):
            estimate_ball_position(malformed, radius_mm=RADIUS, max_residual_rad=1e-6)


@pytest.mark.parametrize("bad_radius", [
    None, True, False, "21.35", [], {}, np.array([21.35]),
])
def test_gate20_malformed_radius_fails_closed(angles, bad_radius):
    rays = tangent_rim([0, 0, 500], angles)
    with pytest.raises(ValueError, match="ball radius"):
        estimate_ball_position(rays, radius_mm=bad_radius, max_residual_rad=1e-6)


@pytest.mark.parametrize("bad_budget", [
    None, True, False, "0.001", [], {}, np.array([0.001]),
    0., -0.1, float("nan"), float("inf"), np.pi / 2,
])
def test_gate20_malformed_residual_budget_fails_closed(angles, bad_budget):
    rays = tangent_rim([0, 0, 500], angles)
    with pytest.raises(ValueError, match="angular residual limit"):
        estimate_ball_position(rays, radius_mm=RADIUS, max_residual_rad=bad_budget)
