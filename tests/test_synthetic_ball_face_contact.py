"""Gate 15: deterministic synthetic ball/planar-face contact tests."""

import numpy as np
import pytest

from openflight.camera.synthetic_ball_face_contact import synthetic_ball_face_contact
from openflight.camera.synthetic_face_frame import SyntheticFaceFrame
from openflight.camera.synthetic_mesh_pose import SyntheticPoseCandidate


FRAME = SyntheticFaceFrame(
    center_model_mm=np.zeros(3),
    heel_to_toe_model=np.array([1., 0., 0.]),
    bottom_to_top_model=np.array([0., 1., 0.]),
    outward_normal_model=np.array([0., 0., 1.]),
)
IDENTITY = SyntheticPoseCandidate(np.eye(3), np.zeros(3))


def test_centered_sphere_touches_face_at_origin():
    result = synthetic_ball_face_contact(
        np.array([0., 0., 21.]), 21., FRAME, IDENTITY
    )
    np.testing.assert_allclose(result.point_world_mm, [0., 0., 0.])
    assert result.heel_to_toe_mm == 0.
    assert result.bottom_to_top_mm == 0.
    assert result.horizontal_region == "center"
    assert result.vertical_region == "center"


@pytest.mark.parametrize(("center", "horizontal", "vertical"), [
    ([12., 5., 21.], "toe", "high"),
    ([-12., -5., 21.], "heel", "low"),
    ([0., 9., 21.], "center", "high"),
])
def test_signed_offsets_and_regions(center, horizontal, vertical):
    result = synthetic_ball_face_contact(
        np.array(center), 21., FRAME, IDENTITY
    )
    assert result.horizontal_region == horizontal
    assert result.vertical_region == vertical
    np.testing.assert_allclose(result.point_world_mm, [center[0], center[1], 0.])


def test_rotated_and_translated_face_contact():
    rotation = np.array([
        [0., 0., 1.], [0., 1., 0.], [-1., 0., 0.]
    ])
    pose = SyntheticPoseCandidate(rotation, np.array([100., 50., 0.]))
    center = np.array([121., 54., 8.])
    result = synthetic_ball_face_contact(center, 21., FRAME, pose)
    assert result.heel_to_toe_mm == pytest.approx(-8.)
    assert result.bottom_to_top_mm == pytest.approx(4.)
    np.testing.assert_allclose(result.point_world_mm, [100., 54., 8.])


@pytest.mark.parametrize("z", [20., 22., -21.])
def test_gap_penetration_and_wrong_side_are_rejected(z):
    with pytest.raises(ValueError, match="tangency"):
        synthetic_ball_face_contact(
            np.array([0., 0., z]), 21., FRAME, IDENTITY
        )


@pytest.mark.parametrize("radius", [0., -1., np.nan, np.inf])
def test_invalid_radius_is_rejected(radius):
    with pytest.raises(ValueError, match="radius"):
        synthetic_ball_face_contact(
            np.array([0., 0., 21.]), radius, FRAME, IDENTITY
        )


def test_invalid_face_frame_is_rejected():
    invalid = SyntheticFaceFrame(
        np.zeros(3), np.array([1., 0., 0.]),
        np.array([1., 0., 0.]), np.array([0., 0., 1.])
    )
    with pytest.raises(ValueError, match="orthonormal"):
        synthetic_ball_face_contact(
            np.array([0., 0., 21.]), 21., invalid, IDENTITY
        )
