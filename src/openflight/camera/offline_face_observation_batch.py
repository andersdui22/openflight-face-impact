"""Gate 21 software-only extraction of synthetic face observations across frames.

This intentionally does not classify real clubfaces or identify contact time.
Every frame must contain one isolated upright synthetic quadrilateral.
"""

from __future__ import annotations

from dataclasses import dataclass

from .synthetic_face_pixel_observation import SyntheticFacePixelObservation
from .synthetic_face_quadrilateral import extract_synthetic_quadrilateral_corners
from .synthetic_frame_candidates import SyntheticFrameCandidate
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class OfflineFaceObservationBatch:
    """Frame-labelled observations and rejected-frame diagnostics."""

    candidates: tuple[SyntheticFrameCandidate, ...]
    observations: tuple[SyntheticFacePixelObservation, ...]
    rejected: tuple[tuple[int, str], ...]
    physical_clubface_confirmed: bool = False

    def __post_init__(self) -> None:
        if self.physical_clubface_confirmed is not False:
            raise ValueError("synthetic observations cannot confirm a real clubface")


def observe_synthetic_face_frames(
    capture: TriggeredCapture,
    frame_indices: tuple[int, ...],
    *,
    image_size: tuple[int, int],
    threshold: int = 180,
    min_area_px: float = 100.0,
    min_fill_ratio: float = 0.85,
    border_margin_px: int = 2,
    max_frames: int = 32,
) -> OfflineFaceObservationBatch:
    """Extract explicitly requested frames; retain failures without guessing.

    A frame with no face, holes, occlusion or multiple bright objects is
    rejected. A valid synthetic rectangle is not a verified golf clubface.
    """
    if not isinstance(capture, TriggeredCapture):
        raise ValueError("typed capture required")
    if (type(max_frames) is not int or max_frames <= 0
            or not isinstance(frame_indices, tuple)
            or not 0 < len(frame_indices) <= max_frames):
        raise ValueError("frame indices must be a nonempty bounded tuple")
    if (any(type(i) is not int or i < 0 or i >= len(capture.frames)
            for i in frame_indices)
            or len(set(frame_indices)) != len(frame_indices)):
        raise ValueError("frame indices must be distinct and within capture")
    candidates = []
    observations = []
    rejected = []
    for index in frame_indices:
        try:
            observed = extract_synthetic_quadrilateral_corners(
                capture, index, image_size=image_size, threshold=threshold,
                min_area_px=min_area_px, min_fill_ratio=min_fill_ratio,
                border_margin_px=border_margin_px,
            )
        except ValueError as exc:
            rejected.append((index, str(exc)))
            continue
        observations.append(observed)
        candidates.append(SyntheticFrameCandidate(index, observed.pixels_px))
    return OfflineFaceObservationBatch(
        tuple(candidates), tuple(observations), tuple(rejected),
    )
