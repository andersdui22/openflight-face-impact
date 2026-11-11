"""Gate 17: named clubface reference points in a documented local frame.

Local +X is toward the toe, +Y toward the crown/topline, +Z points
outward from the striking face. This is a *declared* model convention,
not a measured camera pose or automatic handedness correction.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .club_face_model import ClubFaceModel, FaceSurface


@dataclass(frozen=True)
class PlanarFaceReferences:
    """Named synthetic face-local XYZ-mm points, including geometric center."""

    center_mm: np.ndarray
    heel_mm: np.ndarray
    toe_mm: np.ndarray
    bottom_mm: np.ndarray
    top_mm: np.ndarray


def planar_face_references(model: ClubFaceModel) -> PlanarFaceReferences:
    """Construct planar center and edge midpoints from evidenced dimensions."""
    if not isinstance(model, ClubFaceModel) or not model.geometry_known:
        raise ValueError("explicit dimensioned clubface geometry is required")
    if model.surface is not FaceSurface.PLANAR:
        raise ValueError("reference plane is undefined for curved or unknown faces")
    half_width = model.width_mm / 2
    half_height = model.height_mm / 2
    return PlanarFaceReferences(
        center_mm=np.array([0., 0., 0.]),
        heel_mm=np.array([-half_width, 0., 0.]),
        toe_mm=np.array([half_width, 0., 0.]),
        bottom_mm=np.array([0., -half_height, 0.]),
        top_mm=np.array([0., half_height, 0.]),
    )
