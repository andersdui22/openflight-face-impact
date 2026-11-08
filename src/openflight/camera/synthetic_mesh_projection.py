"""Synthetic-only 3D mesh projection, adapted from OpenFlight clubpose.

Reference: open-flight/openflight PR #250 @ 8d244e25, modules
clubpose/mesh.py (triangle rasterization) and projection.py (pinhole model).
This isolated helper replaces the original fixed radar/rig world frame with
explicit camera intrinsics and world-to-camera extrinsics. No mesh assets.
"""

from dataclasses import dataclass

import cv2
import numpy as np


@dataclass(frozen=True)
class SyntheticCamera:
    """Pinhole intrinsics and world-to-camera transform (millimetres)."""

    width: int
    height: int
    fx: float
    fy: float
    cx: float
    cy: float
    rotation_world_to_camera: np.ndarray
    translation_world_to_camera_mm: np.ndarray


def project_synthetic_mesh(
    vertices_world_mm: np.ndarray,
    triangles: np.ndarray,
    camera: SyntheticCamera,
) -> tuple[np.ndarray, np.ndarray]:
    """Return pixel vertices and a synthetic silhouette; fail closed on bad geometry.

    Camera convention: +z forward, +x image right, +y image down.
    Reject triangles crossing the near plane rather than clipping them.
    """
    vertices = np.asarray(vertices_world_mm, dtype=float)
    faces = np.asarray(triangles)
    rotation = np.asarray(camera.rotation_world_to_camera, dtype=float)
    translation = np.asarray(camera.translation_world_to_camera_mm, dtype=float)
    if vertices.ndim != 2 or vertices.shape[1] != 3 or not vertices.size:
        raise ValueError("vertices must have shape (N, 3)")
    if faces.ndim != 2 or faces.shape[1] != 3 or not np.issubdtype(faces.dtype, np.integer):
        raise ValueError("triangles must have shape (M, 3) with integer indices")
    if not faces.size or np.any(faces < 0) or np.any(faces >= len(vertices)):
        raise ValueError("triangle indices must refer to vertices")
    if rotation.shape != (3, 3) or translation.shape != (3,):
        raise ValueError("camera extrinsics must be a 3x3 rotation and 3-vector")
    parameters = np.array([camera.fx, camera.fy, camera.cx, camera.cy])
    if (not np.all(np.isfinite(vertices)) or not np.all(np.isfinite(rotation))
            or not np.all(np.isfinite(translation)) or not np.all(np.isfinite(parameters))):
        raise ValueError("nonfinite geometry or camera")
    if (type(camera.width) is not int or type(camera.height) is not int
            or camera.width < 1 or camera.height < 1 or camera.fx <= 0 or camera.fy <= 0):
        raise ValueError("invalid camera intrinsics")
    if not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-6):
        raise ValueError("camera rotation must be orthonormal")
    if not np.isclose(np.linalg.det(rotation), 1.0, atol=1e-6):
        raise ValueError("camera rotation must preserve handedness")

    camera_xyz = vertices @ rotation.T + translation
    if np.any(camera_xyz[faces, 2] <= 1e-6):
        raise ValueError("synthetic triangle crosses or lies behind camera")
    uv = np.column_stack((
        camera.fx * camera_xyz[:, 0] / camera_xyz[:, 2] + camera.cx,
        camera.fy * camera_xyz[:, 1] / camera_xyz[:, 2] + camera.cy,
    ))
    if not np.all(np.isfinite(uv)):
        raise ValueError("nonfinite projected vertices")
    mask = np.zeros((camera.height, camera.width), dtype=np.uint8)
    # Equivalent projected-triangle silhouette to OpenFlight's mesh rasterizer.
    # Subpixel vertices are rounded to pixel centres for this fixture-only API.
    for face in faces:
        polygon = np.rint(uv[face]).astype(np.int32)
        cv2.fillConvexPoly(mask, polygon, 1)
    return uv, mask.astype(bool)
