"""Gate 17: synthetic, hardware-free rigid coordinate contract tests."""

import numpy as np
import pytest

from openflight.camera.rigid_frame import RigidFrameTransform


def test_roundtrip_and_composition():
    turn = np.array([[0., -1., 0.], [1., 0., 0.], [0., 0., 1.]])
    camera_from_face = RigidFrameTransform(turn, np.array([12., -3., 400.]))
    face_points = np.array([[0., 0., 0.], [20., 4., 0.]])
    np.testing.assert_allclose(
        camera_from_face.inverse().apply(camera_from_face.apply(face_points)),
        face_points, atol=1e-12,
    )
    parent_from_camera = RigidFrameTransform(np.eye(3), np.array([1., 2., 3.]))
    combined = parent_from_camera.compose(camera_from_face)
    np.testing.assert_allclose(
        combined.apply(face_points),
        parent_from_camera.apply(camera_from_face.apply(face_points)),
    )


def test_translation_units_and_direction():
    transform = RigidFrameTransform(np.eye(3), np.array([10., 20., 30.]))
    np.testing.assert_array_equal(
        transform.apply(np.array([[1., 2., 3.]])),
        np.array([[11., 22., 33.]]),
    )


@pytest.mark.parametrize("rotation", [
    np.zeros((3, 3)),
    np.diag([-1., 1., 1.]),
    np.diag([2., 1., 1.]),
    np.full((3, 3), np.nan),
    np.eye(2),
])
def test_invalid_or_reflected_rotations_rejected(rotation):
    with pytest.raises(ValueError, match="rotation|rigid transform"):
        RigidFrameTransform(rotation, np.zeros(3))


def test_invalid_translation_and_points_rejected():
    with pytest.raises(ValueError, match="finite"):
        RigidFrameTransform(np.eye(3), np.array([0., np.inf, 0.]))
    transform = RigidFrameTransform(np.eye(3), np.zeros(3))
    for points in ([], [[1., 2.]], [[0., 0., np.nan]], [[True, False, True]]):
        with pytest.raises(ValueError, match="finite XYZ-mm"):
            transform.apply(np.asarray(points))


def test_transform_copies_input_arrays():
    rotation = np.eye(3)
    translation = np.array([1., 2., 3.])
    transform = RigidFrameTransform(rotation, translation)
    rotation[0, 0] = 7.
    translation[0] = 99.
    np.testing.assert_array_equal(transform.rotation, np.eye(3))
    np.testing.assert_array_equal(transform.translation_mm, [1., 2., 3.])
    assert not transform.rotation.flags.writeable
    assert not transform.translation_mm.flags.writeable
