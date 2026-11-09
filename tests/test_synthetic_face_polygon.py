"""Gate 17: synthetic polygonal face boundary tests."""

import numpy as np
import pytest

from openflight.camera.synthetic_face_frame import SyntheticFaceFrame
from openflight.camera.synthetic_face_polygon import (
    SyntheticFacePolygon,
    synthetic_polygon_face_contact,
)
from openflight.camera.synthetic_mesh_pose import SyntheticPoseCandidate


FRAME = SyntheticFaceFrame(
    np.zeros(3), np.array([1., 0., 0.]),
    np.array([0., 1., 0.]), np.array([0., 0., 1.])
)
POSE = SyntheticPoseCandidate(np.eye(3), np.zeros(3))
POLYGON = SyntheticFacePolygon(np.array([
    [-50., -25.], [50., -25.], [40., 25.], [-40., 25.]
]))


def contact(x, y, polygon=POLYGON, z=21.):
    return synthetic_polygon_face_contact(
        np.array([x, y, z]), 21., FRAME, POSE, polygon
    )


@pytest.mark.parametrize(("x", "y"), [
    (0., 0.), (-50., -25.), (50., -25.), (40., 25.),
    (-40., 25.), (0., 25.), (45., 0.), (-45., 0.),
])
def test_center_edges_corners_and_asymmetric_sloped_edges(x, y):
    result = contact(x, y)
    assert result.heel_to_toe_mm == x
    assert result.bottom_to_top_mm == y


@pytest.mark.parametrize(("x", "y"), [
    (0., 25.001), (50., 0.), (40., 25.001), (-50., 0.),
])
def test_outside_is_rejected(x, y):
    with pytest.raises(ValueError, match="outside"):
        contact(x, y)


def test_concave_cutout_excludes_point():
    concave = SyntheticFacePolygon(np.array([
        [-4., -4.], [4., -4.], [4., 4.],
        [1., 4.], [1., 0.], [-1., 0.], [-1., 4.], [-4., 4.]
    ]))
    assert contact(0., -2., concave).vertical_region == "low"
    with pytest.raises(ValueError, match="outside"):
        contact(0., 2., concave)
    assert contact(1., 2., concave).heel_to_toe_mm == 1.


@pytest.mark.parametrize("vertices", [
    [[0., 0.], [1., 1.]],
    [[0., 0.], [1., 0.], [2., 0.]],
    [[0., 0.], [1., 0.], [1., 0.], [0., 1.]],
    [[0., 0.], [2., 2.], [0., 2.], [2., 0.]],
    [[0., 0.], [2., 0.], [0., 2.], [2., 2.]],
    [[0., 0.], [1., np.nan], [0., 1.]],
])
def test_invalid_polygon_is_rejected(vertices):
    with pytest.raises(ValueError, match="polygon"):
        contact(0., 0., SyntheticFacePolygon(np.array(vertices)))


def test_non_tangent_ball_is_rejected():
    with pytest.raises(ValueError, match="tangency"):
        contact(0., 0., z=22.)


def test_reversed_polygon_winding_is_supported():
    reversed_polygon = SyntheticFacePolygon(POLYGON.vertices_face_mm[::-1])
    assert contact(0., 0., reversed_polygon).horizontal_region == "center"
