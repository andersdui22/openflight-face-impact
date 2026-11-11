"""Gate 17: explicit rigid transforms for synthetic camera/clubface frames.

Coordinates are right-handed 3D millimeters. This module does not estimate
pose, depth, handedness, or a real clubface from image observations.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RigidFrameTransform:
    """Map local XYZ-mm points into parent XYZ-mm coordinates."""

    rotation: np.ndarray
    translation_mm: np.ndarray

    def __post_init__(self) -> None:
        rotation = np.asarray(self.rotation, dtype=np.float64)
        translation = np.asarray(self.translation_mm, dtype=np.float64)
        if rotation.shape != (3, 3) or translation.shape != (3,):
            raise ValueError("rigid transform requires 3x3 rotation and XYZ-mm translation")
        if not np.isfinite(rotation).all() or not np.isfinite(translation).all():
            raise ValueError("rigid transform must be finite")
        if not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-9, rtol=0):
            raise ValueError("rotation must be orthonormal")
        if not np.isclose(np.linalg.det(rotation), 1.0, atol=1e-9, rtol=0):
            raise ValueError("rotation must be proper, not reflected")
        rotation = rotation.copy()
        translation = translation.copy()
        rotation.setflags(write=False)
        translation.setflags(write=False)
        object.__setattr__(self, "rotation", rotation)
        object.__setattr__(self, "translation_mm", translation)

    def apply(self, points_mm: np.ndarray) -> np.ndarray:
        """Transform a nonempty (N,3) array of finite XYZ-mm positions."""
        points = np.asarray(points_mm)
        if (
            points.ndim != 2
            or points.shape[1] != 3
            or len(points) == 0
            or points.dtype.kind not in "iuf"
            or not np.isfinite(points).all()
        ):
            raise ValueError("points must be nonempty finite XYZ-mm triples")
        return np.asarray(points, dtype=np.float64) @ self.rotation.T + self.translation_mm

    def inverse(self) -> RigidFrameTransform:
        """Return the parent-to-local transform."""
        inverse_rotation = self.rotation.T
        return RigidFrameTransform(
            inverse_rotation, -(inverse_rotation @ self.translation_mm)
        )

    def compose(self, child_to_local: RigidFrameTransform) -> RigidFrameTransform:
        """Return child-to-parent from local-to-parent and child-to-local."""
        if not isinstance(child_to_local, RigidFrameTransform):
            raise ValueError("a rigid child-to-local transform is required")
        return RigidFrameTransform(
            self.rotation @ child_to_local.rotation,
            self.rotation @ child_to_local.translation_mm + self.translation_mm,
        )
