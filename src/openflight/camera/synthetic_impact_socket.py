"""Bounded synthetic-only Face Impact cases for the existing SocketIO server.

All coordinates are known synthetic millimetres; no camera or hardware access.
"""

from dataclasses import asdict

import numpy as np

from .synthetic_face_frame import SyntheticFaceFrame
from .synthetic_face_polygon import SyntheticFacePolygon
from .synthetic_impact_pipeline import calculate_synthetic_face_impact
from .synthetic_mesh_pose import SyntheticPoseCandidate

POLYGON_FACE_MM = [[-50., -25.], [50., -25.], [40., 25.], [-40., 25.]]
_CASES = {
    "toe-high": ("Toe / high", [12., 5., 21.]),
    "heel-low": ("Heel / low", [-12., -5., 21.]),
    "outside-face": ("Outside face", [49., 25., 21.]),
    "no-tangency": ("No tangency", [0., 0., 22.]),
}


def synthetic_face_impact_response(case_id: str) -> dict:
    """Return a versioned synthetic result or explicit error for unknown IDs."""
    if not isinstance(case_id, str) or case_id not in _CASES:
        return {
            "schema_version": 1, "source": "synthetic_python_pipeline",
            "ok": False, "error": "Unknown synthetic case identifier",
        }
    label, center = _CASES[case_id]
    frame = SyntheticFaceFrame(
        np.zeros(3), np.array([1., 0., 0.]),
        np.array([0., 1., 0.]), np.array([0., 0., 1.]),
    )
    pose = SyntheticPoseCandidate(np.eye(3), np.zeros(3))
    polygon = SyntheticFacePolygon(np.asarray(POLYGON_FACE_MM, dtype=float))
    result = calculate_synthetic_face_impact(
        np.asarray(center), 21., frame, pose, polygon,
    )
    fields = asdict(result)
    fields["status"] = result.status.value
    if result.status.value == "ok":
        fields.pop("rejection_reason")
    else:
        for key in ("x_mm", "y_mm", "horizontal_region", "vertical_region"):
            fields.pop(key)
    return {
        "schema_version": 1,
        "source": "synthetic_python_pipeline",
        "ok": True,
        "case_id": case_id,
        "label": label,
        "polygon_face_mm": POLYGON_FACE_MM,
        "result": fields,
    }
