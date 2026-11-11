"""Gate 17/18: reject unsourced, curved and out-of-bounds face references."""

import numpy as np
import pytest

from openflight.camera.club_face_model import ClubFaceModel, ClubFamily, FaceSurface
from openflight.camera.planar_face_reference import planar_face_points_to_camera
from openflight.camera.rigid_frame import RigidFrameTransform


def pose():
    return RigidFrameTransform(np.eye(3), np.array([10., 20., 300.]))


def iron():
    return ClubFaceModel(
        ClubFamily.IRON, "synthetic-iron", FaceSurface.PLANAR,
        width_mm=60., height_mm=30., evidence_source="synthetic-test-fixture",
    )


def test_planar_face_reference_and_boundary_in_mm():
    points = np.array([[0., 0.], [-30., -15.], [30., 15.]])
    np.testing.assert_allclose(
        planar_face_points_to_camera(iron(), pose(), points),
        np.array([[10., 20., 300.], [-20., 5., 300.], [40., 35., 300.]]),
    )


def test_unknown_geometry_rejected():
    with pytest.raises(ValueError, match="dimensioned"):
        planar_face_points_to_camera(
            ClubFaceModel(ClubFamily.WEDGE, "unknown"), pose(), [[0., 0.]]
        )


def test_curved_face_rejected_even_with_dimensions():
    curved = ClubFaceModel(
        ClubFamily.DRIVER, "synthetic-driver", FaceSurface.CURVED,
        width_mm=100., height_mm=45., evidence_source="synthetic-test-fixture",
    )
    with pytest.raises(ValueError, match="curved"):
        planar_face_points_to_camera(curved, pose(), [[0., 0.]])


@pytest.mark.parametrize("points", [
    [[30.01, 0.]], [[0., -15.01]], [[np.nan, 0.]], [[0., 0., 0.]], [],
])
def test_invalid_or_outside_reference_rejected(points):
    with pytest.raises(ValueError, match="outside|finite XY-mm"):
        planar_face_points_to_camera(iron(), pose(), points)


def test_missing_pose_rejected():
    with pytest.raises(ValueError, match="pose"):
        planar_face_points_to_camera(iron(), None, [[0., 0.]])
