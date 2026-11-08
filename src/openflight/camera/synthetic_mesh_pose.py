"""Synthetic silhouette pose matching based on OpenFlight experimental IoU fitting.

Source concept: open-flight/openflight PR #250 @ 8d244e25,
src/openflight/camera/clubpose/fit.py::iou and fit_frame_6dof.
This constrained candidate scorer reuses Gate 11's calibrated projection,
without radar constraints, asset redistribution or physical pose claims.
"""

from dataclasses import dataclass

import numpy as np

from .synthetic_mesh_projection import SyntheticCamera, project_synthetic_mesh


@dataclass(frozen=True)
class SyntheticPoseCandidate:
    """Explicit model-to-world rigid pose; translation units are millimetres."""

    rotation_model_to_world: np.ndarray
    translation_model_to_world_mm: np.ndarray


@dataclass(frozen=True)
class SyntheticPoseResult:
    """Best unambiguous synthetic candidate index and silhouette overlap."""

    candidate_index: int
    intersection_over_union: float


def fit_synthetic_silhouette(
    vertices_model_mm: np.ndarray,
    triangles: np.ndarray,
    camera: SyntheticCamera,
    observed_mask: np.ndarray,
    candidates: tuple[SyntheticPoseCandidate, ...],
    *,
    min_iou: float = 0.8,
    min_margin: float = 0.05,
) -> SyntheticPoseResult:
    """Match a bounded candidate list; reject weak or ambiguous observations.

    This is a discrete synthetic candidate comparison, not a real 6DOF solver.
    """
    observed = np.asarray(observed_mask)
    if (observed.shape != (camera.height, camera.width)
            or observed.dtype != np.bool_ or not np.any(observed)):
        raise ValueError("expected nonempty boolean synthetic observation")
    if (not np.isfinite(min_iou) or not 0 < min_iou <= 1
            or not np.isfinite(min_margin) or not 0 < min_margin <= 1):
        raise ValueError("invalid matching thresholds")
    if not 1 <= len(candidates) <= 128:
        raise ValueError("candidate count must be between 1 and 128")
    vertices = np.asarray(vertices_model_mm, dtype=float)
    if vertices.ndim != 2 or vertices.shape[1] != 3 or not np.all(np.isfinite(vertices)):
        raise ValueError("invalid synthetic model vertices")

    scores = []
    for candidate in candidates:
        rotation = np.asarray(candidate.rotation_model_to_world, dtype=float)
        translation = np.asarray(candidate.translation_model_to_world_mm, dtype=float)
        if (rotation.shape != (3, 3) or translation.shape != (3,)
                or not np.all(np.isfinite(rotation))
                or not np.all(np.isfinite(translation))
                or not np.allclose(rotation.T @ rotation, np.eye(3), atol=1e-6)
                or not np.isclose(np.linalg.det(rotation), 1.0, atol=1e-6)):
            raise ValueError("invalid rigid pose candidate")
        transformed = vertices @ rotation.T + translation
        _, rendered = project_synthetic_mesh(transformed, triangles, camera)
        intersection = np.count_nonzero(rendered & observed)
        union = np.count_nonzero(rendered | observed)
        scores.append(float(intersection / union) if union else 0.0)

    order = np.argsort(np.asarray(scores))[::-1]
    best = int(order[0])
    if scores[best] < min_iou:
        raise ValueError("no sufficiently matching synthetic pose")
    if len(order) > 1 and scores[best] - scores[int(order[1])] < min_margin:
        raise ValueError("ambiguous synthetic pose candidates")
    return SyntheticPoseResult(best, scores[best])
