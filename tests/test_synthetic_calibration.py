"""Hardware-free verification of synthetic planar calibration."""

import numpy as np
import pytest

from openflight.camera.synthetic_calibration import SyntheticPlanarCalibration


def test_known_reference_mapping_and_inverse():
    pixels = np.array([[100, 200], [200, 200], [100, 300], [200, 300]])
    millimeters = np.array([[0, 0], [50, 0], [0, -25], [50, -25]])
    calibration = SyntheticPlanarCalibration.from_references(pixels, millimeters)
    samples = np.array([[150, 250], [125, 225]])
    np.testing.assert_allclose(
        calibration.to_millimeters(samples), [[25, -12.5], [12.5, -6.25]], atol=1e-10
    )
    np.testing.assert_allclose(
        calibration.to_pixels(calibration.to_millimeters(samples)), samples, atol=1e-10
    )


@pytest.mark.parametrize(
    "pixels,millimeters",
    [
        ([[0, 0], [1, 1]], [[0, 0], [1, 1]]),
        ([[0, 0], [1, 1], [2, 2]], [[0, 0], [1, 0], [0, 1]]),
        ([[0, 0], [1, 0], [0, 1]], [[0, 0], [0, 0], [0, 0]]),
        ([[0, 0], [1, 0], [0, float("nan")]], [[0, 0], [1, 0], [0, 1]]),
        ([[0, 0], [1, 0], [0, 1], [1, 1]], [[0, 0], [1, 0], [0, 1], [3, 3]]),
    ],
)
def test_invalid_references_rejected(pixels, millimeters):
    with pytest.raises(ValueError):
        SyntheticPlanarCalibration.from_references(pixels, millimeters)


def test_nonfinite_query_rejected():
    calibration = SyntheticPlanarCalibration.from_references(
        [[0, 0], [1, 0], [0, 1]], [[0, 0], [1, 0], [0, 1]]
    )
    with pytest.raises(ValueError):
        calibration.to_millimeters([[float("inf"), 0]])
    with pytest.raises(ValueError):
        calibration.to_pixels([[0, float("nan")]])
