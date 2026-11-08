"""Fixture-only tests for conservative synthetic IR face region localization."""

import numpy as np
import pytest

from openflight.camera.synthetic_ir_face import locate_synthetic_ir_face


def _fixture():
    frame = np.zeros((80, 120), dtype=np.uint8)
    frame[20:51, 40:71] = 230
    return frame


def test_locates_synthetic_face_bounds_and_center():
    face = locate_synthetic_ir_face(_fixture())
    assert face.bounds == (40, 20, 70, 50)
    assert face.center == (55.0, 35.0)


def test_below_threshold_fails_closed():
    with pytest.raises(ValueError, match="No bright"):
        locate_synthetic_ir_face(_fixture(), threshold=240)


def test_extra_reflection_fails_closed():
    frame = _fixture()
    frame[5, 5] = 255
    with pytest.raises(ValueError, match="exactly one"):
        locate_synthetic_ir_face(frame)


def test_missing_face_fails_closed():
    with pytest.raises(ValueError, match="No bright"):
        locate_synthetic_ir_face(np.zeros((80, 120), dtype=np.uint8))


def test_incomplete_rectangle_fails_closed():
    frame = _fixture()
    frame[30, 55] = 0
    with pytest.raises(ValueError, match="exactly one"):
        locate_synthetic_ir_face(frame)


@pytest.mark.parametrize("bad", [np.zeros((0, 4), dtype=np.uint8), np.zeros((4, 4, 3), dtype=np.uint8), np.zeros((4, 4), dtype=np.float32)])
def test_invalid_frame_fails_closed(bad):
    with pytest.raises(ValueError, match="grayscale"):
        locate_synthetic_ir_face(bad)


@pytest.mark.parametrize("threshold", [0, 256, 1.5, True])
def test_invalid_threshold_fails_closed(threshold):
    with pytest.raises(ValueError, match="Threshold"):
        locate_synthetic_ir_face(_fixture(), threshold=threshold)
