"""Hardware-free tests for strictly annotated synthetic ball/face images."""

import numpy as np
import pytest

from openflight.camera.synthetic_localization import locate_synthetic_ball_and_face


def synthetic_frame():
    """Draw a red disk and green rectangle with exact integer geometry."""
    frame = np.zeros((64, 96, 3), dtype=np.uint8)
    yy, xx = np.ogrid[:64, :96]
    frame[(xx - 20) ** 2 + (yy - 30) ** 2 <= 6**2] = (255, 0, 0)
    frame[12:29, 60:82] = (0, 255, 0)
    return frame


def test_exact_synthetic_ball_and_face_positions():
    ball, face = locate_synthetic_ball_and_face(synthetic_frame())
    assert ball.center == (20.0, 30.0)
    assert ball.bounds == (14, 24, 26, 36)
    assert face.center == (70.5, 20.0)
    assert face.bounds == (60, 12, 81, 28)


@pytest.mark.parametrize("shape", [(10, 10), (0, 10, 3), (10, 10, 4), (10,)])
def test_invalid_image_shapes(shape):
    with pytest.raises(ValueError, match="RGB frame"):
        locate_synthetic_ball_and_face(np.zeros(shape, dtype=np.uint8))


def test_invalid_dtype():
    with pytest.raises(ValueError, match="uint8"):
        locate_synthetic_ball_and_face(synthetic_frame().astype(float))


def test_missing_ball_or_face():
    frame = synthetic_frame()
    frame[np.all(frame == (255, 0, 0), axis=2)] = 0
    with pytest.raises(ValueError, match="missing"):
        locate_synthetic_ball_and_face(frame)
    frame = synthetic_frame()
    frame[np.all(frame == (0, 255, 0), axis=2)] = 0
    with pytest.raises(ValueError, match="missing"):
        locate_synthetic_ball_and_face(frame)


def test_second_ball_marker_is_rejected():
    frame = synthetic_frame()
    frame[4, 4] = (255, 0, 0)
    with pytest.raises(ValueError, match="ambiguous|disk"):
        locate_synthetic_ball_and_face(frame)


def test_incomplete_face_marker_is_rejected():
    frame = synthetic_frame()
    frame[20, 70] = 0
    with pytest.raises(ValueError, match="ambiguous"):
        locate_synthetic_ball_and_face(frame)


def test_non_circular_ball_marker_is_rejected():
    frame = synthetic_frame()
    frame[30, 20] = 0
    with pytest.raises(ValueError, match="ambiguous"):
        locate_synthetic_ball_and_face(frame)
