"""Hardware-free integration tests for synthetic image-frame calibration."""

import numpy as np
import pytest

from openflight.camera.synthetic_calibration import SyntheticPlanarCalibration
from openflight.camera.synthetic_frame_calibration import map_frame_points_to_millimeters


@pytest.fixture
def calibration():
    pixels = np.array([[0, 0], [10, 0], [0, 10], [10, 10]])
    millimeters = np.array([[5, -3], [25, -3], [5, 27], [25, 27]])
    return SyntheticPlanarCalibration.from_references(pixels, millimeters)


def test_grayscale_frame_maps_known_points(calibration):
    frame = np.zeros((20, 30), dtype=np.uint8)
    result = map_frame_points_to_millimeters(frame, [[0, 0], [10, 10], [29, 19]], calibration)
    np.testing.assert_allclose(result, [[5, -3], [25, 27], [63, 54]])


def test_color_frame_and_empty_point_set(calibration):
    frame = np.zeros((20, 30, 3), dtype=np.uint8)
    result = map_frame_points_to_millimeters(frame, np.empty((0, 2)), calibration)
    assert result.shape == (0, 2)


@pytest.mark.parametrize("shape", [(0, 10), (10, 0), (10,), (10, 10, 0), (2, 3, 4, 5)])
def test_invalid_frame_shapes_fail_closed(shape, calibration):
    with pytest.raises(ValueError, match="frame"):
        map_frame_points_to_millimeters(np.zeros(shape), [[1, 1]], calibration)


@pytest.mark.parametrize("points", [
    [[-1, 0]], [[0, -1]], [[30, 0]], [[0, 20]],
    [[np.nan, 1]], [[np.inf, 1]], [[1]], [1, 2],
])
def test_invalid_or_outside_points_fail_closed(points, calibration):
    with pytest.raises(ValueError, match="pixel|Pixel"):
        map_frame_points_to_millimeters(np.zeros((20, 30)), points, calibration)
