"""Synthetic-only tests for calibrated 3D projection (Gate 11)."""

import numpy as np
import pytest

from openflight.camera.synthetic_mesh_projection import (
    SyntheticCamera,
    project_synthetic_mesh,
)


def camera(**changes):
    values = dict(
        width=100, height=80, fx=100.0, fy=100.0, cx=50.0, cy=40.0,
        rotation_world_to_camera=np.eye(3),
        translation_world_to_camera_mm=np.zeros(3),
    )
    values.update(changes)
    return SyntheticCamera(**values)


VERTICES = np.array([[-1., -1., 10.], [1., -1., 10.], [0., 1., 10.]])
FACES = np.array([[0, 1, 2]])


def test_centered_triangle_projects_and_rasterizes():
    uv, mask = project_synthetic_mesh(VERTICES, FACES, camera())
    np.testing.assert_allclose(uv, [[40., 30.], [60., 30.], [50., 50.]])
    assert mask.shape == (80, 100)
    assert mask[40, 50]
    assert not mask[0, 0]


def test_translation_moves_projected_triangle():
    base, _ = project_synthetic_mesh(VERTICES, FACES, camera())
    shifted, _ = project_synthetic_mesh(
        VERTICES, FACES,
        camera(translation_world_to_camera_mm=np.array([1., 0., 0.])),
    )
    np.testing.assert_allclose(shifted[:, 0] - base[:, 0], 10.0)


def test_rotation_changes_projected_coordinates():
    rotation = np.diag([-1., -1., 1.])
    original, _ = project_synthetic_mesh(VERTICES, FACES, camera())
    rotated, _ = project_synthetic_mesh(
        VERTICES, FACES, camera(rotation_world_to_camera=rotation)
    )
    np.testing.assert_allclose(rotated[:, 0], 100 - original[:, 0])
    np.testing.assert_allclose(rotated[:, 1], 80 - original[:, 1])


@pytest.mark.parametrize("vertices,faces,cam", [
    (VERTICES * np.array([1., 1., -1.]), FACES, camera()),
    (VERTICES, np.array([[0, 1, 9]]), camera()),
    (VERTICES, FACES, camera(fx=0)),
    (VERTICES, FACES, camera(rotation_world_to_camera=np.zeros((3, 3)))),
    (np.array([[np.nan, 0., 10.], [1., 0., 10.], [0., 1., 10.]]), FACES, camera()),
])
def test_invalid_geometry_or_calibration_fails_closed(vertices, faces, cam):
    with pytest.raises(ValueError):
        project_synthetic_mesh(vertices, faces, cam)
