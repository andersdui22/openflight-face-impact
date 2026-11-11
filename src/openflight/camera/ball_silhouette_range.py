"""Offline sphere range from calibrated silhouette rays and an explicit radius.

The radius / sin(half angle) calculation follows located_tee_range in
HarjotDhanota/openflight ea95a64329e5bbea52f901e3badb1cb07995a6fc,
src/openflight/camera/resting_ball_range.py (AGPL-3.0-or-later).
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BallSilhouettePosition:
    """Candidate sphere centre in right/down/forward camera millimetres."""

    center_camera_mm: np.ndarray
    range_mm: float
    angular_radius_rad: float
    max_residual_rad: float


def _unit_edge_rays(edge_rays: np.ndarray) -> np.ndarray:
    rays = np.asarray(edge_rays)
    if rays.ndim != 2 or rays.shape[1] != 3 or len(rays) < 5:
        raise ValueError("at least five silhouette rays in an (N, 3) array are required")
    if rays.dtype.kind not in "iuf" or not np.all(np.isfinite(rays)) or np.any(rays[:, 2] <= 0):
        raise ValueError("silhouette rays must be finite numeric forward directions")
    rays = rays.astype(np.float64)
    with np.errstate(over="ignore"):
        norms = np.linalg.norm(rays, axis=1)
    if not np.allclose(norms, 1.0, rtol=0, atol=1e-6):
        raise ValueError("silhouette rays must have unit length")
    rays = rays / norms[:, None]
    if len(np.unique(rays, axis=0)) != len(rays):
        raise ValueError("silhouette rays must be distinct")
    return rays


def _cone_axis(rays: np.ndarray) -> np.ndarray:
    centroid = rays.mean(axis=0)
    # A tangent ray has a constant dot product with the centre direction.
    _, values, basis = np.linalg.svd(rays - centroid, full_matrices=False)
    if values[1] <= max(values[0] * 1e-6, 1e-12):
        raise ValueError("silhouette rays do not constrain a cone axis")
    axis = basis[-1]
    if axis @ centroid < 0:
        axis = -axis
    return axis


def _require_rim_coverage(axis: np.ndarray, rays: np.ndarray) -> None:
    radial = rays - (rays @ axis)[:, None] * axis
    lengths = np.linalg.norm(radial, axis=1)
    if np.any(lengths <= 1e-12):
        raise ValueError("silhouette contains a ray on the cone axis")
    reference = radial[0] / lengths[0]
    angles = np.sort(np.arctan2(radial @ np.cross(axis, reference), radial @ reference))
    gaps = np.diff(angles, append=angles[0] + 2 * math.pi)
    if gaps.max() >= math.pi:
        raise ValueError("silhouette rays must cover more than half the rim")


def estimate_ball_position(
    edge_rays: np.ndarray,
    *,
    radius_mm: float,
    max_residual_rad: float,
) -> BallSilhouettePosition:
    """Estimate the centre from an observed tangent cone and known sphere radius.

    Provide at least five distinct, calibrated unit rays to the silhouette.
    The caller supplies an angular residual budget in radians. The returned
    residual checks consistency with a sphere, not physical measurement accuracy.
    """
    if (
        isinstance(radius_mm, (bool, str, bytes))
        or not isinstance(radius_mm, (int, float, np.integer, np.floating))
        or not math.isfinite(radius_mm)
        or radius_mm <= 0
    ):
        raise ValueError("ball radius must be positive and finite")
    if (
        isinstance(max_residual_rad, (bool, str, bytes))
        or not isinstance(max_residual_rad, (int, float, np.integer, np.floating))
        or not math.isfinite(max_residual_rad)
        or not 0 < max_residual_rad < math.pi / 2
    ):
        raise ValueError("angular residual limit must be between zero and pi/2")
    rays = _unit_edge_rays(edge_rays)
    axis = _cone_axis(rays)
    cosines = rays @ axis
    if np.any(cosines <= 0) or axis[2] <= 0:
        raise ValueError("silhouette rays do not form a forward cone")
    angles = np.arctan2(np.linalg.norm(np.cross(rays, axis), axis=1), cosines)
    half_angle = float(angles.mean())
    if half_angle <= max(max_residual_rad, 1e-8):
        raise ValueError("angular radius is too small for the residual budget")
    residual = float(np.max(np.abs(angles - half_angle)))
    if residual > max_residual_rad:
        raise ValueError("silhouette rays disagree with a spherical rim")
    _require_rim_coverage(axis, rays)
    distance = radius_mm / math.sin(half_angle)
    center = axis * distance
    if not np.all(np.isfinite(center)) or center[2] <= radius_mm:
        raise ValueError("estimated sphere must be finite and in front of the camera")
    return BallSilhouettePosition(center, distance, half_angle, residual)
