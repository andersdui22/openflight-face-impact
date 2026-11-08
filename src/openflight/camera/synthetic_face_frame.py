"""Explicit synthetic clubface-local coordinate frame (millimetres).

Coordinates: local x increases heel -> toe; local y bottom -> top;
local z follows cross(x, y), perpendicular to the face. These are
model conventions only, not physical handedness or a calibrated clubhead.
"""

from dataclasses import dataclass

import numpy as np

from .synthetic_mesh_pose import SyntheticPoseCandidate


@dataclass(frozen=True)
class SyntheticFaceFrame:
    """A model-space origin and right-handed orthonormal face axes."""

    center_model_mm: np.ndarray
    heel_to_toe_model: np.ndarray
    bottom_to_top_model: np.ndarray
    outward_normal_model: np.ndarray


def _vector(value: np.ndarray, name: str) -> np.ndarray:
    result = np.asarray(value, dtype=float)
    if result.shape != (3,) or not np.all(np.isfinite(result)):
        raise ValueError(f"invalid {name}: expected finite 3-vector")
    return result


def _rotation(candidate: SyntheticPoseCandidate) -> tuple[np.ndarray, np.ndarray]:
    rotation = np.asarray(candidate.rotation_model_to_world, dtype=float)
    translation = _vector(candidate.translation_model_to_world_mm, "translation")
    if (rotation.shape != (3, 3) or not np.all(np.isfinite(rotation))
            or not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-6)
            or not np.isclose(np.linalg.det(rotation), 1., atol=1e-6)):
        raise ValueError("invalid rigid pose rotation")
    return rotation, translation


def _axes(frame: SyntheticFaceFrame) -> tuple[np.ndarray, np.ndarray]:
    center = _vector(frame.center_model_mm, "face center")
    x_axis = _vector(frame.heel_to_toe_model, "heel-to-toe axis")
    y_axis = _vector(frame.bottom_to_top_model, "bottom-to-top axis")
    z_axis = _vector(frame.outward_normal_model, "outward normal")
    basis = np.column_stack((x_axis, y_axis, z_axis))
    if (not np.allclose(basis.T @ basis, np.eye(3), atol=1e-6)
            or not np.isclose(np.linalg.det(basis), 1., atol=1e-6)):
        raise ValueError("face axes must be right-handed and orthonormal")
    return center, basis


def world_to_synthetic_face(
    point_world_mm: np.ndarray,
    frame: SyntheticFaceFrame,
    pose: SyntheticPoseCandidate,
) -> np.ndarray:
    """Convert a world-space 3D point to (heel-to-toe, vertical, normal) mm."""
    point = _vector(point_world_mm, "world point")
    center, basis = _axes(frame)
    rotation, translation = _rotation(pose)
    point_model = (point - translation) @ rotation
    return (point_model - center) @ basis


def synthetic_face_to_world(
    point_face_mm: np.ndarray,
    frame: SyntheticFaceFrame,
    pose: SyntheticPoseCandidate,
) -> np.ndarray:
    """Convert a synthetic local face coordinate back to world millimetres."""
    point = _vector(point_face_mm, "face point")
    center, basis = _axes(frame)
    rotation, translation = _rotation(pose)
    point_model = center + point @ basis.T
    return point_model @ rotation.T + translation
