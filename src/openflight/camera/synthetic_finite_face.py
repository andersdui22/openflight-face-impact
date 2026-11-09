"""Finite rectangular bounds for synthetic clubface tangent points.

Reuses Gate 15 sphere/plane contact. Face dimensions are explicit synthetic
millimetres, not measured real clubhead dimensions or accuracy evidence.
"""

from dataclasses import dataclass

import numpy as np

from .synthetic_ball_face_contact import (
    SyntheticContact,
    synthetic_ball_face_contact,
)
from .synthetic_face_frame import SyntheticFaceFrame
from .synthetic_mesh_pose import SyntheticPoseCandidate


@dataclass(frozen=True)
class SyntheticFaceDimensions:
    """Explicit centered rectangular face size in millimetres."""

    width_mm: float
    height_mm: float


def synthetic_finite_face_contact(
    ball_center_world_mm: np.ndarray,
    ball_radius_mm: float,
    frame: SyntheticFaceFrame,
    pose: SyntheticPoseCandidate,
    dimensions: SyntheticFaceDimensions,
    *,
    tolerance_mm: float = 1e-6,
) -> SyntheticContact:
    """Return Gate 15 tangency only when it lies inside finite face bounds.

    Edges and corners are included. Tolerance is used only for the sphere
    tangency test; boundary checks are exact to avoid admitting outside hits.
    """
    width = np.asarray(dimensions.width_mm)
    height = np.asarray(dimensions.height_mm)
    for value in (width, height):
        if (value.ndim != 0 or not np.issubdtype(value.dtype, np.number)
                or not np.isfinite(value) or value <= 0):
            raise ValueError("face dimensions must be positive finite mm")
    contact = synthetic_ball_face_contact(
        ball_center_world_mm, ball_radius_mm, frame, pose,
        tolerance_mm=tolerance_mm,
    )
    if (abs(contact.heel_to_toe_mm) > float(width) / 2
            or abs(contact.bottom_to_top_mm) > float(height) / 2):
        raise ValueError("synthetic contact lies outside finite face bounds")
    return contact
