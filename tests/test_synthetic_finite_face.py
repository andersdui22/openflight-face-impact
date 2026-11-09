"""Gate 16: finite synthetic face bounds tests."""

import numpy as np
import pytest

from openflight.camera.synthetic_face_frame import SyntheticFaceFrame
from openflight.camera.synthetic_finite_face import (
    SyntheticFaceDimensions,
    synthetic_finite_face_contact,
)
from openflight.camera.synthetic_mesh_pose import SyntheticPoseCandidate


FRAME = SyntheticFaceFrame(
    np.zeros(3), np.array([1., 0., 0.]),
    np.array([0., 1., 0.]), np.array([0., 0., 1.])
)
POSE = SyntheticPoseCandidate(np.eye(3), np.zeros(3))
DIMENSIONS = SyntheticFaceDimensions(width_mm=100., height_mm=50.)


@pytest.mark.parametrize(("x", "y"), [
    (0., 0.), (50., 0.), (-50., 0.),
    (0., 25.), (0., -25.),
    (50., 25.), (-50., -25.), (-50., 25.), (50., -25.),
])
def test_center_edges_and_corners_are_included(x, y):
    result = synthetic_finite_face_contact(
        np.array([x, y, 21.]), 21., FRAME, POSE, DIMENSIONS
    )
    assert result.heel_to_toe_mm == x
    assert result.bottom_to_top_mm == y
    np.testing.assert_allclose(result.point_world_mm, [x, y, 0.])


@pytest.mark.parametrize(("x", "y"), [
    (50.001, 0.), (-50.001, 0.),
    (0., 25.001), (0., -25.001), (50.001, 25.001),
])
def test_outside_face_is_rejected(x, y):
    with pytest.raises(ValueError, match="outside"):
        synthetic_finite_face_contact(
            np.array([x, y, 21.]), 21., FRAME, POSE, DIMENSIONS
        )


@pytest.mark.parametrize(("width", "height"), [
    (0., 50.), (-10., 50.), (100., 0.), (100., -1.),
    (np.nan, 50.), (100., np.inf),
])
def test_invalid_dimensions_are_rejected(width, height):
    with pytest.raises(ValueError, match="dimensions"):
        synthetic_finite_face_contact(
            np.array([0., 0., 21.]), 21., FRAME, POSE,
            SyntheticFaceDimensions(width, height)
        )


def test_reuses_gate15_tangency_rejection():
    with pytest.raises(ValueError, match="tangency"):
        synthetic_finite_face_contact(
            np.array([0., 0., 22.]), 21., FRAME, POSE, DIMENSIONS
        )


def test_rotated_face_preserves_local_bounds():
    rotation = np.array([
        [0., 0., 1.], [0., 1., 0.], [-1., 0., 0.]
    ])
    pose = SyntheticPoseCandidate(rotation, np.array([100., 50., 0.]))
    result = synthetic_finite_face_contact(
        np.array([121., 60., -20.]), 21., FRAME, pose, DIMENSIONS
    )
    assert result.heel_to_toe_mm == pytest.approx(20.)
    assert result.bottom_to_top_mm == pytest.approx(10.)
