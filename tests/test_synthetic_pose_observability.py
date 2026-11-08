"""Gate 13: single-camera synthetic observability regression tests."""

import numpy as np
import pytest

from openflight.camera.synthetic_mesh_pose import SyntheticPoseCandidate
from openflight.camera.synthetic_mesh_projection import (
    SyntheticCamera,
    project_synthetic_mesh,
)
from openflight.camera.synthetic_pose_observability import (
    analyze_synthetic_observability,
)


CAMERA = SyntheticCamera(
    width=120, height=100, fx=100., fy=100., cx=60., cy=50.,
    rotation_world_to_camera=np.eye(3),
    translation_world_to_camera_mm=np.zeros(3),
)
VERTICES = np.array([[-2., -1., 10.], [2., -1., 10.], [0., 2., 10.]])
FACES = np.array([[0, 1, 2]])


def pose(x=0., rotation=None):
    return SyntheticPoseCandidate(
        np.eye(3) if rotation is None else rotation,
        np.array([x, 0., 0.]),
    )


def observed():
    return project_synthetic_mesh(VERTICES, FACES, CAMERA)[1]


def test_clear_translation_is_observable():
    result = analyze_synthetic_observability(
        VERTICES, FACES, CAMERA, observed(), (pose(0.), pose(3.))
    )
    assert result.is_observable
    assert result.best_candidate_index == 0
    assert result.best_iou == 1.
    assert not result.ambiguous_candidate_indices


def test_distinct_depth_axis_rotations_can_be_indistinguishable():
    # A triangle symmetric around x=0 projects identically after a 180 degree
    # rotation about its in-plane vertical axis only if the model is planar.
    rotation = np.diag([-1., 1., -1.])
    # Use an intentionally symmetric planar rectangular silhouette instead.
    vertices = np.array([
        [-2., -1., 10.], [2., -1., 10.],
        [2., 1., 10.], [-2., 1., 10.],
    ])
    faces = np.array([[0, 1, 2], [0, 2, 3]])
    # Rotate in model coordinates at z=0 then translate model to z=10.
    vertices[:, 2] = 0.
    center_pose = SyntheticPoseCandidate(np.eye(3), np.array([0., 0., 10.]))
    reversed_pose = SyntheticPoseCandidate(rotation, np.array([0., 0., 10.]))
    reference = project_synthetic_mesh(
        vertices + np.array([0., 0., 10.]), faces, CAMERA
    )[1]
    result = analyze_synthetic_observability(
        vertices, faces, CAMERA, reference, (center_pose, reversed_pose)
    )
    assert not result.is_observable
    assert result.best_iou == 1.
    assert result.runner_up_iou == 1.
    assert result.iou_margin == 0.
    assert result.ambiguous_candidate_indices == (1,)


def test_rejects_weak_match_without_guessing():
    mask = np.zeros((100, 120), dtype=bool)
    mask[2:5, 2:5] = True
    result = analyze_synthetic_observability(
        VERTICES, FACES, CAMERA, mask, (pose(),)
    )
    assert not result.is_observable
    assert result.best_iou < 0.8


@pytest.mark.parametrize("mask", [
    np.zeros((100, 120), dtype=bool),
    np.ones((99, 120), dtype=bool),
    np.ones((100, 120), dtype=np.uint8),
])
def test_invalid_observations_fail_closed(mask):
    with pytest.raises(ValueError, match="observation"):
        analyze_synthetic_observability(
            VERTICES, FACES, CAMERA, mask, (pose(),)
        )


def test_invalid_rotation_fails_closed():
    with pytest.raises(ValueError, match="rigid pose"):
        analyze_synthetic_observability(
            VERTICES, FACES, CAMERA, observed(),
            (pose(rotation=np.zeros((3, 3))),)
        )


def test_candidate_bound_is_enforced():
    with pytest.raises(ValueError, match="candidate count"):
        analyze_synthetic_observability(
            VERTICES, FACES, CAMERA, observed(), (pose(),) * 129
        )
