"""Gate 18: synthetic Face Impact pipeline success and rejection tests."""

import numpy as np
import pytest

from openflight.camera.synthetic_face_frame import SyntheticFaceFrame
from openflight.camera.synthetic_face_polygon import SyntheticFacePolygon
from openflight.camera.synthetic_impact_pipeline import (
    SyntheticImpactStatus,
    calculate_synthetic_face_impact,
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


def impact(center, radius=21., frame=FRAME, pose=POSE, polygon=POLYGON):
    return calculate_synthetic_face_impact(
        np.asarray(center, dtype=float), radius, frame, pose, polygon
    )


@pytest.mark.parametrize(("center", "x", "y", "horizontal", "vertical"), [
    ([0., 0., 21.], 0., 0., "center", "center"),
    ([12., 5., 21.], 12., 5., "toe", "high"),
    ([-12., -5., 21.], -12., -5., "heel", "low"),
])
def test_valid_contact_result(center, x, y, horizontal, vertical):
    result = impact(center)
    assert result.status is SyntheticImpactStatus.OK
    assert result.x_mm == x
    assert result.y_mm == y
    assert result.horizontal_region == horizontal
    assert result.vertical_region == vertical
    assert result.rejection_reason is None


def test_rotated_translated_pose_result():
    rotation = np.array([
        [0., 0., 1.], [0., 1., 0.], [-1., 0., 0.]
    ])
    pose = SyntheticPoseCandidate(rotation, np.array([100., 50., 0.]))
    result = impact([121., 54., 8.], pose=pose)
    assert result.status is SyntheticImpactStatus.OK
    assert result.x_mm == pytest.approx(-8.)
    assert result.y_mm == pytest.approx(4.)


def test_outside_polygon_returns_explicit_rejection():
    result = impact([49., 25., 21.])
    assert result.status is SyntheticImpactStatus.OUTSIDE_FACE
    assert result.x_mm is None and result.y_mm is None
    assert result.horizontal_region is None
    assert result.rejection_reason is not None


@pytest.mark.parametrize("z", [20., 22., -21.])
def test_non_tangency_returns_explicit_rejection(z):
    result = impact([0., 0., z])
    assert result.status is SyntheticImpactStatus.NO_TANGENCY
    assert result.x_mm is None
    assert result.vertical_region is None


def test_invalid_radius_returns_invalid_geometry():
    result = impact([0., 0., 21.], radius=-1.)
    assert result.status is SyntheticImpactStatus.INVALID_GEOMETRY
    assert result.x_mm is None


def test_invalid_polygon_returns_invalid_geometry():
    polygon = SyntheticFacePolygon(np.array([
        [0., 0.], [1., 1.], [2., 2.]
    ]))
    result = impact([0., 0., 21.], polygon=polygon)
    assert result.status is SyntheticImpactStatus.INVALID_GEOMETRY
    assert result.y_mm is None


@pytest.mark.parametrize("kwargs", [
    {"status": SyntheticImpactStatus.OK, "x_mm": 1., "y_mm": None,
     "horizontal_region": "toe", "vertical_region": "center"},
    {"status": SyntheticImpactStatus.OK, "x_mm": float("nan"), "y_mm": 0.,
     "horizontal_region": "toe", "vertical_region": "center"},
    {"status": SyntheticImpactStatus.OK, "x_mm": 1., "y_mm": 0.,
     "horizontal_region": "toe", "vertical_region": "center",
     "rejection_reason": "contradiction"},
    {"status": SyntheticImpactStatus.OUTSIDE_FACE, "x_mm": 1.,
     "rejection_reason": "outside"},
    {"status": SyntheticImpactStatus.NO_TANGENCY, "horizontal_region": "heel",
     "rejection_reason": "no contact"},
    {"status": SyntheticImpactStatus.INVALID_GEOMETRY},
])
def test_gates23_24_reject_contradictory_impact_results(kwargs):
    from openflight.camera.synthetic_impact_pipeline import SyntheticImpactResult

    with pytest.raises(ValueError):
        SyntheticImpactResult(**kwargs)


@pytest.mark.parametrize(("horizontal", "vertical"), [
    (" ", "center"),
    ("toe", "\\t"),
    ("", "high"),
    ("heel", "  "),
])
def test_gate24_rejects_blank_accepted_impact_regions(horizontal, vertical):
    from openflight.camera.synthetic_impact_pipeline import SyntheticImpactResult

    with pytest.raises(ValueError, match="accepted synthetic impact"):
        SyntheticImpactResult(
            status=SyntheticImpactStatus.OK,
            x_mm=0., y_mm=0.,
            horizontal_region=horizontal, vertical_region=vertical,
        )
