"""Hardware-free tests for automatic synthetic rectangle proposals."""

import cv2
import numpy as np
import pytest

from openflight.camera.synthetic_face_proposal import propose_synthetic_ir_face_region


def _fixture():
    frame = np.zeros((160, 240), dtype=np.uint8)
    cv2.circle(frame, (48, 65), 14, 255, -1)
    frame[80:111, 150:191] = 230
    return frame


def test_finds_rectangle_without_supplied_crop_and_ignores_round_ball():
    result = propose_synthetic_ir_face_region(_fixture())
    assert result.bounds == (150, 80, 190, 110)
    assert result.center == (170.0, 95.0)


def test_missing_rectangle_fails_closed():
    frame = _fixture()
    frame[80:111, 150:191] = 0
    with pytest.raises(ValueError, match="exactly one"):
        propose_synthetic_ir_face_region(frame)


def test_two_rectangles_are_ambiguous():
    frame = _fixture()
    frame[15:26, 180:201] = 230
    with pytest.raises(ValueError, match="exactly one"):
        propose_synthetic_ir_face_region(frame)


def test_incomplete_rectangle_is_not_a_candidate():
    frame = _fixture()
    frame[90, 170] = 0
    with pytest.raises(ValueError, match="exactly one"):
        propose_synthetic_ir_face_region(frame)


def test_edge_touching_rectangle_is_rejected():
    frame = _fixture()
    frame[80:111, 150:191] = 0
    frame[0:31, 150:191] = 230
    with pytest.raises(ValueError, match="edge"):
        propose_synthetic_ir_face_region(frame)


def test_below_threshold_rectangle_fails_closed():
    with pytest.raises(ValueError, match="exactly one"):
        propose_synthetic_ir_face_region(_fixture(), threshold=240)


@pytest.mark.parametrize("threshold", [0, 256, True, 1.5])
def test_invalid_threshold_fails_closed(threshold):
    with pytest.raises(ValueError, match="Threshold"):
        propose_synthetic_ir_face_region(_fixture(), threshold=threshold)


@pytest.mark.parametrize("shape", [(0, 10), (10, 10, 3)])
def test_invalid_frame_fails_closed(shape):
    with pytest.raises(ValueError, match="grayscale"):
        propose_synthetic_ir_face_region(np.zeros(shape, dtype=np.uint8))
