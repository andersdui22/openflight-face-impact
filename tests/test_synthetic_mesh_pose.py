"""Gate 12 deterministic synthetic pose-matching tests."""

import numpy as np
import pytest

from openflight.camera.synthetic_mesh_pose import (
    SyntheticPoseCandidate,
    fit_synthetic_silhouette,
)
from openflight.camera.synthetic_mesh_projection import (
    SyntheticCamera,
    project_synthetic_mesh,
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
        rotation_model_to_world=np.eye(3) if rotation is None else rotation,
        translation_model_to_world_mm=np.array([x, 0., 0.]),
    )


def observation():
    return project_synthetic_mesh(VERTICES, FACES, CAMERA)[1]


def test_recovers_known_synthetic_translation():
    result = fit_synthetic_silhouette(
        VERTICES, FACES, CAMERA, observation(), (pose(2.), pose(0.), pose(-2.))
    )
    assert result.candidate_index == 1
    assert result.intersection_over_union == 1.0


def test_rejects_duplicate_equivalent_poses():
    with pytest.raises(ValueError, match="ambiguous"):
        fit_synthetic_silhouette(
            VERTICES, FACES, CAMERA, observation(), (pose(), pose())
        )


def test_rejects_nonmatching_observation():
    mask = np.zeros((100, 120), dtype=bool)
    mask[5:10, 5:10] = True
    with pytest.raises(ValueError, match="no sufficiently"):
        fit_synthetic_silhouette(VERTICES, FACES, CAMERA, mask, (pose(),))


def test_rejects_invalid_candidate_rotation():
    with pytest.raises(ValueError, match="rigid pose"):
        fit_synthetic_silhouette(
            VERTICES, FACES, CAMERA, observation(),
            (pose(rotation=np.zeros((3, 3))),)
        )


@pytest.mark.parametrize("mask", [
    np.zeros((100, 120), dtype=bool),
    np.ones((99, 120), dtype=bool),
    np.ones((100, 120), dtype=np.uint8),
])
def test_rejects_invalid_observation(mask):
    with pytest.raises(ValueError, match="observation"):
        fit_synthetic_silhouette(VERTICES, FACES, CAMERA, mask, (pose(),))


def test_rejects_unbounded_candidate_search():
    with pytest.raises(ValueError, match="candidate count"):
        fit_synthetic_silhouette(
            VERTICES, FACES, CAMERA, observation(), (pose(),) * 129
        )
