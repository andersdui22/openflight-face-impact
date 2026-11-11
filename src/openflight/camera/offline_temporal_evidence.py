"""Gate 22/24 offline evidence gate for capture timing and frame selection.

Only synthetic candidate geometry is selected; physical contact is unknown.
"""

from __future__ import annotations

from dataclasses import dataclass

from .offline_frame_selection import (
    OfflineFrameSelection, OfflineSelectionStatus, select_unique_synthetic_frame,
)
from .offline_frame_spacing import OfflineFrameSpacing, assess_offline_frame_spacing
from .synthetic_frame_candidates import AssessedFrameCandidate
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class OfflineTemporalEvidence:
    """Combined timing and synthetic frame-selection evidence."""

    spacing: OfflineFrameSpacing
    selection: OfflineFrameSelection
    accepted_for_offline_analysis: bool
    physical_contact_confirmed: bool = False

    def __post_init__(self) -> None:
        if self.physical_contact_confirmed is not False:
            raise ValueError("offline evidence cannot confirm physical contact")
        expected = (
            self.spacing.accepted
            and self.selection.status is OfflineSelectionStatus.UNIQUE_SYNTHETIC
        )
        if self.accepted_for_offline_analysis is not expected:
            raise ValueError("offline evidence acceptance contradicts quality gates")


def assess_offline_temporal_evidence(
    capture: TriggeredCapture,
    candidates: tuple[AssessedFrameCandidate, ...],
    *,
    max_sensor_gap_ns: int,
    max_host_gap_ns: int,
    max_frames: int = 32,
) -> OfflineTemporalEvidence:
    """Compose existing validators without inventing impact or clock alignment.

    Even one unique synthetic candidate cannot pass when timing gaps fail.
    The frame selection remains visible for diagnosis, but its frame index
    must not be interpreted as a measured contact instant.
    """
    spacing = assess_offline_frame_spacing(
        capture, max_sensor_gap_ns=max_sensor_gap_ns,
        max_host_gap_ns=max_host_gap_ns,
    )
    selection = select_unique_synthetic_frame(candidates, max_frames=max_frames)
    if any(item.frame_index >= len(capture.frames) for item in candidates):
        raise ValueError("candidate frame index exceeds capture frame count")
    return OfflineTemporalEvidence(
        spacing=spacing,
        selection=selection,
        accepted_for_offline_analysis=(
            spacing.accepted
            and selection.status is OfflineSelectionStatus.UNIQUE_SYNTHETIC
        ),
    )
