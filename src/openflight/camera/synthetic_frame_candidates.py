"""Gates 20-24: bounded offline multi-frame synthetic candidate assessment.

Evaluating several explicit candidates does not select the physical contact
instant. Every face observation remains externally supplied synthetic data.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .capture_ball_synthetic_quality import (
    AssessedSyntheticCaptureImpact,
    assess_capture_ball_synthetic_impact,
)
from .checkerboard_calibration import CheckerboardCalibration
from .synthetic_face_polygon import SyntheticFacePolygon
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class SyntheticFrameCandidate:
    """Explicit frame identity and externally supplied labelled face pixels."""

    frame_index: int
    face_pixels_px: np.ndarray

    def __post_init__(self) -> None:
        if (not isinstance(self.frame_index, int)
                or isinstance(self.frame_index, bool)
                or self.frame_index < 0):
            raise ValueError("candidate frame index must be nonnegative integer")
        pixels = np.asarray(self.face_pixels_px)
        if (pixels.ndim != 2 or pixels.shape[1] != 2
                or pixels.dtype.kind not in "iuf"
                or not np.all(np.isfinite(pixels))):
            raise ValueError("candidate face pixels must be finite Nx2 numeric")
        copied = np.array(pixels, dtype=np.float64, copy=True)
        copied.setflags(write=False)
        object.__setattr__(self, "face_pixels_px", copied)


@dataclass(frozen=True)
class AssessedFrameCandidate:
    """An explicit candidate's synthetic assessment; not contact selection."""

    frame_index: int
    assessment: AssessedSyntheticCaptureImpact


def assess_synthetic_frame_candidates(  # pylint: disable=too-many-arguments
    calibration: CheckerboardCalibration,
    capture: TriggeredCapture,
    candidates: tuple[SyntheticFrameCandidate, ...],
    landmarks_face_mm: np.ndarray,
    polygon: SyntheticFacePolygon,
    *,
    ball_radius_mm: float,
    max_ball_residual_rad: float,
    max_face_rms_px: float,
    min_face_margin_px: float,
    contact_tolerance_mm: float,
    threshold: int,
    min_area_px: float,
    ball_border_margin_px: float,
    min_circularity: float = 0.0,
    max_candidates: int = 32,
) -> tuple[AssessedFrameCandidate, ...]:
    """Assess distinct explicitly supplied frames; never choose impact time.

    Input contract errors are raised before any candidate is evaluated.
    Geometry failures for individual candidates are returned as rejected
    synthetic results, with their original frame indices.
    """
    if (not isinstance(max_candidates, int)
            or isinstance(max_candidates, bool)
            or max_candidates <= 0):
        raise ValueError("max_candidates must be positive integer")
    if (not isinstance(candidates, tuple)
            or not 0 < len(candidates) <= max_candidates):
        raise ValueError("candidate batch must be nonempty and bounded tuple")
    if any(not isinstance(item, SyntheticFrameCandidate) for item in candidates):
        raise ValueError("candidate batch requires SyntheticFrameCandidate entries")
    indices = [item.frame_index for item in candidates]
    if len(indices) != len(set(indices)):
        raise ValueError("candidate batch contains duplicate frame indices")
    return tuple(
        AssessedFrameCandidate(
            frame_index=item.frame_index,
            assessment=assess_capture_ball_synthetic_impact(
                calibration, capture, item.frame_index,
                landmarks_face_mm, item.face_pixels_px, polygon,
                ball_radius_mm=ball_radius_mm,
                max_ball_residual_rad=max_ball_residual_rad,
                max_face_rms_px=max_face_rms_px,
                min_face_margin_px=min_face_margin_px,
                contact_tolerance_mm=contact_tolerance_mm,
                threshold=threshold,
                min_area_px=min_area_px,
                ball_border_margin_px=ball_border_margin_px,
                min_circularity=min_circularity,
                face_observation_frame_index=item.frame_index,
            ),
        )
        for item in candidates
    )
