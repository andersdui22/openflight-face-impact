"""Guard the offline optical ray contract using known synthetic optics."""

from dataclasses import replace

import cv2 as cv
import numpy as np
import pytest

from openflight.camera.calibrated_rays import calibrated_pixel_rays
from openflight.camera.checkerboard_calibration import CheckerboardCalibration

SIZE = (640, 400)


@pytest.fixture
def calibration():
    return CheckerboardCalibration(
        SIZE,
        np.array([[530.0, 0, 315], [0, 525.0, 198], [0, 0, 1]]),
        np.array([-0.24, 0.08, 0.002, -0.003, 0.01]),
        0.1,
        (0.1, 0.1, 0.1),
    )


def test_known_distorted_directions_are_recovered_in_input_order(calibration):
    scene = np.array([[0, 0, 1], [-0.5, 0.28, 1], [0.49, -0.29, 1]])
    pixels, _ = cv.projectPoints(
        scene, np.zeros(3), np.zeros(3), calibration.camera_matrix, calibration.distortion
    )
    rays = calibrated_pixel_rays(calibration, pixels.reshape(-1, 2), image_size=SIZE)
    np.testing.assert_allclose(rays, scene / np.linalg.norm(scene, axis=1, keepdims=True), atol=1e-9)
    np.testing.assert_allclose(np.linalg.norm(rays, axis=1), 1)


@pytest.mark.parametrize("point", [[-0.1, 20], [640, 20], [10, -0.1], [10, 400]])
def test_outside_observations_are_rejected(calibration, point):
    with pytest.raises(ValueError, match="outside"):
        calibrated_pixel_rays(calibration, np.array([point]), image_size=SIZE)


def test_pixel_zero_and_last_pixel_are_valid_for_an_ideal_model(calibration):
    ideal = replace(calibration, distortion=np.zeros(5))
    rays = calibrated_pixel_rays(ideal, np.array([[0, 0], [639, 399]]), image_size=SIZE)
    assert np.all(rays[:, 2] > 0)
    assert np.all(rays[0, :2] < 0) and np.all(rays[1, :2] > 0)


@pytest.mark.parametrize("size", [(400, 640), (1280, 800), (640.0, 400)])
def test_calibration_cannot_be_applied_to_another_resolution(calibration, size):
    with pytest.raises(ValueError, match="dimensions"):
        calibrated_pixel_rays(calibration, np.array([[20, 20]]), image_size=size)


@pytest.mark.parametrize("pixels", [[], [10, 20], [[np.nan, 1]], [[True, False]]])
def test_malformed_pixel_inputs_are_rejected(calibration, pixels):
    with pytest.raises(ValueError, match="finite column/row"):
        calibrated_pixel_rays(calibration, np.array(pixels), image_size=SIZE)


def test_inconsistent_optics_are_rejected(calibration):
    for invalid in (replace(calibration, camera_matrix=np.eye(2)),
                    replace(calibration, distortion=np.array([0, 0, 0, 0, np.inf]))):
        with pytest.raises(ValueError, match="matrix|distortion"):
            calibrated_pixel_rays(invalid, np.array([[20, 20]]), image_size=SIZE)


def test_uninvertible_model_does_not_return_a_ray(calibration):
    severe = replace(calibration, distortion=np.array([-2, 0, 0, 0, 0]))
    with pytest.raises(ValueError, match="did not converge|locally folded"):
        calibrated_pixel_rays(severe, np.array([[639, 399]]), image_size=SIZE)
