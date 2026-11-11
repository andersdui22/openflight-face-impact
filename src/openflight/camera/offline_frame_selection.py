"""Offline evidence-only candidate selection for Phase 5 Gate 22/24.

This selects a uniquely admissible *synthetic geometry* frame, not a measured
contact instant. Multiple accepted frames are ambiguous, not an invitation to
guess based on capture order or host timestamps.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .synthetic_frame_candidates import AssessedFrameCandidate
from .synthetic_impact_pipeline import SyntheticImpactStatus


class OfflineSelectionStatus(str, Enum):
    """Evidence-only outcomes; none certifies physical contact timing."""

    UNIQUE_SYNTHETIC = "unique_synthetic"
    NO_ACCEPTED_FRAME = "no_accepted_frame"
    AMBIGUOUS = "ambiguous"


@dataclass(frozen=True)
class OfflineFrameSelection:
    """A unique synthetic candidate or a fail-closed nonselection."""

    status: OfflineSelectionStatus
    frame_index: int | None
    accepted_frame_indices: tuple[int, ...]
    reason: str
    physical_contact_confirmed: bool = False

    def __post_init__(self) -> None:
        if self.physical_contact_confirmed is not False:
            raise ValueError("offline selection cannot confirm physical contact")
        if not isinstance(self.status, OfflineSelectionStatus):
            raise ValueError("invalid offline selection status")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("selection requires a reason")
        if (not isinstance(self.accepted_frame_indices, tuple)
                or any(not isinstance(i, int) or isinstance(i, bool) or i < 0
                       for i in self.accepted_frame_indices)
                or len(set(self.accepted_frame_indices)) != len(self.accepted_frame_indices)):
            raise ValueError("invalid accepted frame identities")
        if self.status is OfflineSelectionStatus.UNIQUE_SYNTHETIC:
            if (len(self.accepted_frame_indices) != 1
                    or self.frame_index != self.accepted_frame_indices[0]):
                raise ValueError("unique selection requires exactly one accepted frame")
        elif self.frame_index is not None:
            raise ValueError("ambiguous or rejected selection cannot expose frame index")


def select_unique_synthetic_frame(
    frames: tuple[AssessedFrameCandidate, ...],
    *,
    max_frames: int = 32,
) -> OfflineFrameSelection:
    """Select only a uniquely accepted synthetic frame, never a contact time.

    Validate all records before choosing. No ranking by timestamp, frame index,
    fabricated confidence, or distance from the trigger is performed.
    """
    if (not isinstance(max_frames, int) or isinstance(max_frames, bool)
            or max_frames <= 0):
        raise ValueError("max_frames must be a positive integer")
    if not isinstance(frames, tuple) or not 0 < len(frames) <= max_frames:
        raise ValueError("frames must be a nonempty bounded tuple")

    seen: set[int] = set()
    accepted: list[int] = []
    for item in frames:
        if not isinstance(item, AssessedFrameCandidate):
            raise ValueError("invalid frame assessment entry")
        index = item.frame_index
        if not isinstance(index, int) or isinstance(index, bool) or index < 0:
            raise ValueError("invalid frame identity")
        if index in seen:
            raise ValueError("duplicate frame identity")
        seen.add(index)
        assessment = item.assessment
        if (assessment is None or not hasattr(assessment, "impact")
                or not hasattr(assessment, "quality")):
            raise ValueError("invalid frame assessment")
        impact, quality = assessment.impact, assessment.quality
        if (not hasattr(impact, "status")
                or not isinstance(impact.status, SyntheticImpactStatus)
                or not isinstance(quality.accepted_synthetic_geometry, bool)
                or quality.physically_validated is not False
                or quality.position_uncertainty_mm is not None
                or quality.accepted_synthetic_geometry !=
                (impact.status is SyntheticImpactStatus.OK)):
            raise ValueError("inconsistent synthetic frame quality")
        if impact.status is SyntheticImpactStatus.OK:
            accepted.append(index)

    identities = tuple(sorted(accepted))
    if len(identities) == 1:
        return OfflineFrameSelection(
            OfflineSelectionStatus.UNIQUE_SYNTHETIC, identities[0], identities,
            "one frame has accepted synthetic geometry; physical contact unverified",
        )
    if not identities:
        return OfflineFrameSelection(
            OfflineSelectionStatus.NO_ACCEPTED_FRAME, None, identities,
            "no candidate has accepted synthetic geometry",
        )
    return OfflineFrameSelection(
        OfflineSelectionStatus.AMBIGUOUS, None, identities,
        "multiple frames have accepted synthetic geometry; contact frame unobservable",
    )
