"""Gate 17: reference-point directions and fail-closed geometry tests."""

import numpy as np
import pytest

from openflight.camera.club_face_model import ClubFaceModel, ClubFamily, FaceSurface
from openflight.camera.face_reference_points import planar_face_references
from openflight.camera.planar_face_reference import planar_face_points_to_camera
from openflight.camera.rigid_frame import RigidFrameTransform


def test_named_reference_points_match_planar_face_bounds():
    model = ClubFaceModel(
        ClubFamily.WEDGE, "synthetic-wedge", FaceSurface.PLANAR,
        width_mm=60., height_mm=30., evidence_source="synthetic-test-fixture",
    )
    refs = planar_face_references(model)
    np.testing.assert_array_equal(refs.center_mm, [0., 0., 0.])
    np.testing.assert_array_equal(refs.heel_mm, [-30., 0., 0.])
    np.testing.assert_array_equal(refs.toe_mm, [30., 0., 0.])
    np.testing.assert_array_equal(refs.bottom_mm, [0., -15., 0.])
    np.testing.assert_array_equal(refs.top_mm, [0., 15., 0.])
    pose = RigidFrameTransform(np.eye(3), np.array([0., 0., 200.]))
    xy = np.stack([refs.center_mm[:2], refs.heel_mm[:2], refs.toe_mm[:2]])
    np.testing.assert_array_equal(
        planar_face_points_to_camera(model, pose, xy),
        np.array([[0., 0., 200.], [-30., 0., 200.], [30., 0., 200.]]),
    )


def test_reference_points_require_evidenced_planar_face():
    with pytest.raises(ValueError, match="dimensioned"):
        planar_face_references(ClubFaceModel(ClubFamily.IRON, "unknown"))
    with pytest.raises(ValueError, match="plane"):
        planar_face_references(ClubFaceModel(
            ClubFamily.DRIVER, "synthetic-driver", FaceSurface.CURVED,
            width_mm=90., height_mm=40., evidence_source="synthetic-test-fixture",
        ))
