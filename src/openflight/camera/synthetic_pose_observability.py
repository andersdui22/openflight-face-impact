"""Synthetic one-camera pose observability for a bounded candidate set.

Builds on Gate 11 projection and Gate 12 silhouette IoU concept.
No real camera, calibrated physical angular error, or full 6DOF claim.
"""

from dataclasses import dataclass

import numpy as np

from .synthetic_mesh_pose import SyntheticPoseCandidate
from .synthetic_mesh_projection import SyntheticCamera, project_synthetic_mesh


@dataclass(frozen=True)
class SyntheticObservability:
    """Candidate-set-specific synthetic ambiguity and overlap metrics."""

    best_candidate_index: int
    best_iou: float
    runner_up_iou: float
    iou_margin: float
    ambiguous_candidate_indices: tuple[int, ...]
    is_observable: bool


def analyze_synthetic_observability(
    vertices_model_mm: np.ndarray,
    triangles: np.ndarray,
    camera: SyntheticCamera,
    observed_mask: np.ndarray,
    candidates: tuple[SyntheticPoseCandidate, ...],
    *,
    min_iou: float = 0.8,
    min_margin: float = 0.05,
) -> SyntheticObservability:
    """Score all synthetic poses, including near-identical 2D silhouettes.

    An unobservable result is a measurement outcome, not an estimated pose.
    """
    observed = np.asarray(observed_mask)
    if (observed.shape != (camera.height, camera.width)
            or observed.dtype != np.bool_ or not np.any(observed)):
        raise ValueError("expected nonempty boolean synthetic observation")
    if (not np.isfinite(min_iou) or not 0 < min_iou <= 1
            or not np.isfinite(min_margin) or not 0 < min_margin <= 1):
        raise ValueError("invalid observability thresholds")
    if not 1 <= len(candidates) <= 128:
        raise ValueError("candidate count must be between 1 and 128")
    vertices = np.asarray(vertices_model_mm, dtype=float)
    if (vertices.ndim != 2 or vertices.shape[1] != 3
            or not np.all(np.isfinite(vertices))):
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
        union = np.count_nonzero(rendered | observed)
        intersection = np.count_nonzero(rendered & observed)
        scores.append(float(intersection / union) if union else 0.0)

    ranked = sorted(range(len(scores)), key=lambda index: (-scores[index], index))
    best = ranked[0]
    runner_up = scores[ranked[1]] if len(ranked) > 1 else 0.0
    margin = scores[best] - runner_up if len(ranked) > 1 else 1.0
    ambiguous = tuple(
        index for index in ranked[1:]
        if scores[best] - scores[index] < min_margin
    )
    observable = scores[best] >= min_iou and not ambiguous
    return SyntheticObservability(
        best, scores[best], runner_up, margin, ambiguous, observable
    )
