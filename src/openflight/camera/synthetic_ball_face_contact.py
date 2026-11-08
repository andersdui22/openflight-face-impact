"""Synthetic sphere-to-infinite-plane clubface tangency in millimetres.

Uses the Gate 14 face frame. This is an exact geometry fixture only:
no real ball tracking, collision dynamics or finite clubface boundaries.
"""

from dataclasses import dataclass

import numpy as np

from .synthetic_face_frame import (
    SyntheticFaceFrame,
    world_to_synthetic_face,
)
from .synthetic_mesh_pose import SyntheticPoseCandidate


@dataclass(frozen=True)
class SyntheticContact:
    """Local tangent location, signed heel/toe and vertical offsets (mm)."""

    heel_to_toe_mm: float
    bottom_to_top_mm: float
    point_world_mm: np.ndarray
    horizontal_region: str
    vertical_region: str


def synthetic_ball_face_contact(
    ball_center_world_mm: np.ndarray,
    ball_radius_mm: float,
    frame: SyntheticFaceFrame,
    pose: SyntheticPoseCandidate,
    *,
    tolerance_mm: float = 1e-6,
    center_band_mm: float = 1e-6,
) -> SyntheticContact:
    """Return a contact only for a sphere tangent to the face's outward side.

    The ball center must lie at +radius along the face's local outward normal.
    A sphere separated from or penetrating the infinite plane is not contact.
    """
    radius = np.asarray(ball_radius_mm)
    tolerance = np.asarray(tolerance_mm)
    band = np.asarray(center_band_mm)
    if (radius.ndim != 0 or not np.issubdtype(radius.dtype, np.number)
            or not np.isfinite(radius) or radius <= 0):
        raise ValueError("ball radius must be a positive finite scalar in mm")
    if (tolerance.ndim != 0 or not np.issubdtype(tolerance.dtype, np.number)
            or not np.isfinite(tolerance) or tolerance < 0
            or band.ndim != 0 or not np.issubdtype(band.dtype, np.number)
            or not np.isfinite(band) or band < 0):
        raise ValueError("invalid contact tolerance or center band")
    center = np.asarray(ball_center_world_mm, dtype=float)
    local = world_to_synthetic_face(center, frame, pose)
    if abs(local[2] - float(radius)) > float(tolerance):
        raise ValueError("no unique synthetic sphere-plane tangency")
    point = center - float(radius) * (
        np.asarray(frame.outward_normal_model, dtype=float)
        @ np.asarray(pose.rotation_model_to_world, dtype=float).T
    )
    horizontal = ("center" if abs(local[0]) <= band
                  else "toe" if local[0] > 0 else "heel")
    vertical = ("center" if abs(local[1]) <= band
                else "high" if local[1] > 0 else "low")
    return SyntheticContact(
        float(local[0]), float(local[1]), point, horizontal, vertical
    )
