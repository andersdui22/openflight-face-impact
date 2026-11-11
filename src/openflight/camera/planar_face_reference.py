"""Gate 17/18: bounded, synthetic planar clubface reference mapping.

Only explicitly planar, dimensioned face models can be mapped to the
face-local XY plane. Curved faces need a separately evidenced surface model.
No camera pose, depth, impact measurement or physical accuracy is inferred.
"""

from __future__ import annotations

import numpy as np

from .club_face_model import ClubFaceModel, FaceSurface
from .rigid_frame import RigidFrameTransform


def planar_face_points_to_camera(
    model: ClubFaceModel,
    camera_from_face: RigidFrameTransform,
    face_xy_mm: np.ndarray,
) -> np.ndarray:
    """Map bounded face-local XY-mm observations to synthetic camera XYZ-mm."""
    if not isinstance(model, ClubFaceModel) or not model.geometry_known:
        raise ValueError("explicit dimensioned clubface geometry is required")
    if model.surface is not FaceSurface.PLANAR:
        raise ValueError("curved clubface requires an evidenced surface model")
    if not isinstance(camera_from_face, RigidFrameTransform):
        raise ValueError("explicit camera-from-face pose is required")
    points = np.asarray(face_xy_mm)
    if (
        points.ndim != 2 or points.shape[1] != 2 or len(points) == 0
        or points.dtype.kind not in "iuf" or not np.isfinite(points).all()
    ):
        raise ValueError("face coordinates must be nonempty finite XY-mm pairs")
    points = np.asarray(points, dtype=np.float64)
    if np.any(np.abs(points[:, 0]) > model.width_mm / 2) or np.any(
        np.abs(points[:, 1]) > model.height_mm / 2
    ):
        raise ValueError("face coordinate is outside evidenced model bounds")
    face_xyz = np.column_stack((points, np.zeros(len(points))))
    return camera_from_face.apply(face_xyz)
