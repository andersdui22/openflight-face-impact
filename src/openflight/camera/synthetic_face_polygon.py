"""Synthetic polygonal face footprint with strict geometry validation.

Polygon coordinates are local heel-to-toe and bottom-to-top millimetres.
The face is a planar synthetic fixture, not an actual clubhead mesh.
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
class SyntheticFacePolygon:
    """Vertices of a simple face polygon, in local (x, y) mm."""

    vertices_face_mm: np.ndarray


def _cross(a: np.ndarray, b: np.ndarray, c: np.ndarray) -> float:
    ab = b - a
    ac = c - a
    return float(ab[0] * ac[1] - ab[1] * ac[0])


def _on_segment(a: np.ndarray, b: np.ndarray, p: np.ndarray) -> bool:
    return (_cross(a, b, p) == 0.
            and min(a[0], b[0]) <= p[0] <= max(a[0], b[0])
            and min(a[1], b[1]) <= p[1] <= max(a[1], b[1]))


def _intersects(a: np.ndarray, b: np.ndarray,
                c: np.ndarray, d: np.ndarray) -> bool:
    x1, x2 = _cross(a, b, c), _cross(a, b, d)
    y1, y2 = _cross(c, d, a), _cross(c, d, b)
    if ((x1 > 0 > x2 or x1 < 0 < x2)
            and (y1 > 0 > y2 or y1 < 0 < y2)):
        return True
    return (x1 == 0. and _on_segment(a, b, c)
            or x2 == 0. and _on_segment(a, b, d)
            or y1 == 0. and _on_segment(c, d, a)
            or y2 == 0. and _on_segment(c, d, b))


def _validated_vertices(polygon: SyntheticFacePolygon) -> np.ndarray:
    vertices = np.asarray(polygon.vertices_face_mm, dtype=float)
    if (vertices.ndim != 2 or vertices.shape[1:] != (2,)
            or not 3 <= len(vertices) <= 128
            or not np.all(np.isfinite(vertices))):
        raise ValueError("invalid polygon: expected 3-128 finite 2D vertices")
    if any(np.array_equal(vertices[i], vertices[(i + 1) % len(vertices)])
           for i in range(len(vertices))):
        raise ValueError("invalid polygon: zero-length edge")
    signed_area = float(np.sum(
        vertices[:, 0] * np.roll(vertices[:, 1], -1)
        - vertices[:, 1] * np.roll(vertices[:, 0], -1)
    ))
    if not np.isfinite(signed_area) or signed_area == 0.:
        raise ValueError("invalid polygon: degenerate area")
    n = len(vertices)
    for i in range(n):
        for j in range(i + 1, n):
            if j == i + 1 or (i == 0 and j == n - 1):
                continue
            if _intersects(
                vertices[i], vertices[(i + 1) % n],
                vertices[j], vertices[(j + 1) % n],
            ):
                raise ValueError("invalid polygon: self-intersecting boundary")
    return vertices


def _contains(vertices: np.ndarray, point: np.ndarray) -> bool:
    inside = False
    x, y = point
    for i in range(len(vertices)):
        a, b = vertices[i], vertices[(i + 1) % len(vertices)]
        if _on_segment(a, b, point):
            return True
        if (a[1] > y) != (b[1] > y):
            x_intersection = a[0] + (y - a[1]) * (
                b[0] - a[0]) / (b[1] - a[1])
            if x < x_intersection:
                inside = not inside
    return inside


def synthetic_polygon_face_contact(
    ball_center_world_mm: np.ndarray,
    ball_radius_mm: float,
    frame: SyntheticFaceFrame,
    pose: SyntheticPoseCandidate,
    polygon: SyntheticFacePolygon,
    *,
    tolerance_mm: float = 1e-6,
) -> SyntheticContact:
    """Return Gate 15 tangent contact only inside the simple face polygon."""
    vertices = _validated_vertices(polygon)
    contact = synthetic_ball_face_contact(
        ball_center_world_mm, ball_radius_mm, frame, pose,
        tolerance_mm=tolerance_mm,
    )
    point = np.array([contact.heel_to_toe_mm, contact.bottom_to_top_mm])
    if not _contains(vertices, point):
        raise ValueError("synthetic contact lies outside polygonal face")
    return contact
