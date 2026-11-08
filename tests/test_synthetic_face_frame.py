"""Gate 14: deterministic synthetic clubface coordinate-frame tests."""

import numpy as np
import pytest

from openflight.camera.synthetic_face_frame import (
    SyntheticFaceFrame,
    synthetic_face_to_world,
    world_to_synthetic_face,
)
from openflight.camera.synthetic_mesh_pose import SyntheticPoseCandidate


def face_frame():
    return SyntheticFaceFrame(
        center_model_mm=np.array([2., 3., 4.]),
        heel_to_toe_model=np.array([1., 0., 0.]),
        bottom_to_top_model=np.array([0., 1., 0.]),
        outward_normal_model=np.array([0., 0., 1.]),
    )


def pose(rotation=None, translation=None):
    return SyntheticPoseCandidate(
        np.eye(3) if rotation is None else rotation,
        np.zeros(3) if translation is None else translation,
    )


def test_identity_pose_uses_face_center_as_origin():
    result = world_to_synthetic_face(
        np.array([12., 8., 4.]), face_frame(), pose()
    )
    np.testing.assert_allclose(result, [10., 5., 0.])


def test_off_plane_point_retains_signed_normal_distance():
    result = world_to_synthetic_face(
        np.array([2., 3., 9.]), face_frame(), pose()
    )
    np.testing.assert_allclose(result, [0., 0., 5.])


def test_rotated_translated_pose_round_trip():
    quarter_turn = np.array([
        [0., -1., 0.], [1., 0., 0.], [0., 0., 1.]
    ])
    transformed = pose(
        rotation=quarter_turn,
        translation=np.array([20., -10., 5.]),
    )
    local = np.array([-8., 6., 1.5])
    world = synthetic_face_to_world(local, face_frame(), transformed)
    recovered = world_to_synthetic_face(world, face_frame(), transformed)
    np.testing.assert_allclose(recovered, local, atol=1e-10)


def test_rejects_mirrored_face_basis():
    frame = SyntheticFaceFrame(
        np.zeros(3), np.array([1., 0., 0.]),
        np.array([0., 1., 0.]), np.array([0., 0., -1.])
    )
    with pytest.raises(ValueError, match="right-handed"):
        world_to_synthetic_face(np.zeros(3), frame, pose())


def test_rejects_nonorthogonal_face_basis():
    frame = SyntheticFaceFrame(
        np.zeros(3), np.array([1., 0., 0.]),
        np.array([1., 0., 0.]), np.array([0., 0., 1.])
    )
    with pytest.raises(ValueError, match="orthonormal"):
        world_to_synthetic_face(np.zeros(3), frame, pose())


def test_rejects_invalid_pose_rotation():
    with pytest.raises(ValueError, match="rigid pose"):
        world_to_synthetic_face(
            np.zeros(3), face_frame(), pose(rotation=np.zeros((3, 3)))
        )


@pytest.mark.parametrize("point", [
    np.array([1., 2.]),
    np.array([np.nan, 0., 0.]),
])
def test_rejects_invalid_points(point):
    with pytest.raises(ValueError, match="world point"):
        world_to_synthetic_face(point, face_frame(), pose())
