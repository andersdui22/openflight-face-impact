"""Gate 23/24 fail-closed offline impact evidence export.

This is a typed, synthetic-only handoff for later phases, not a physical
impact event or calibrated uncertainty estimate.
"""

from __future__ import annotations

from dataclasses import dataclass

from .offline_temporal_evidence import OfflineTemporalEvidence
from .synthetic_frame_candidates import AssessedFrameCandidate
from .synthetic_impact_pipeline import SyntheticImpactStatus
from .triggered_buffer import TriggeredCapture


@dataclass(frozen=True)
class OfflineImpactEvidence:
    """Result with provenance and explicit synthetic-only limitations."""

    shot_id: str
    session_id: str
    frame_index: int | None
    accepted_for_offline_analysis: bool
    x_mm: float | None
    y_mm: float | None
    horizontal_region: str | None
    vertical_region: str | None
    reason: str
    physically_validated: bool = False
    position_uncertainty_mm: float | None = None

    def __post_init__(self) -> None:
        if (not isinstance(self.shot_id, str) or not self.shot_id.strip()
                or not isinstance(self.session_id, str) or not self.session_id.strip()):
            raise ValueError("impact evidence requires capture identity")
        if self.physically_validated is not False or self.position_uncertainty_mm is not None:
            raise ValueError("offline evidence cannot assert physical accuracy")
        coordinates = (self.x_mm, self.y_mm, self.horizontal_region, self.vertical_region)
        if self.accepted_for_offline_analysis:
            if self.frame_index is None or any(value is None for value in coordinates):
                raise ValueError("accepted offline evidence requires coordinates and frame")
        elif self.frame_index is not None or any(value is not None for value in coordinates):
            raise ValueError("rejected offline evidence cannot expose impact coordinates")
        if not isinstance(self.reason, str) or not self.reason.strip():
            raise ValueError("impact evidence requires an explanation")


def export_offline_impact_evidence(
    capture: TriggeredCapture,
    candidates: tuple[AssessedFrameCandidate, ...],
    temporal: OfflineTemporalEvidence,
) -> OfflineImpactEvidence:
    """Export only a temporally accepted unique synthetic impact candidate."""
    if not isinstance(temporal, OfflineTemporalEvidence):
        raise ValueError("offline export requires temporal evidence")
    if not isinstance(candidates, tuple) or not candidates:
        raise ValueError("offline export requires nonempty candidate assessments")
    indices = tuple(sorted(
        item.frame_index for item in candidates
        if item.assessment.impact.status is SyntheticImpactStatus.OK
    ))
    if indices != temporal.selection.accepted_frame_indices:
        raise ValueError("temporal evidence does not match impact candidates")
    if temporal.accepted_for_offline_analysis:
        index = temporal.selection.frame_index
        matches = [item for item in candidates if item.frame_index == index]
        if len(matches) != 1:
            raise ValueError("selected frame not uniquely present in candidates")
        result = matches[0].assessment.impact
        quality = matches[0].assessment.quality
        if (result.status is not SyntheticImpactStatus.OK
                or quality.accepted_synthetic_geometry is not True
                or quality.physically_validated is not False
                or quality.position_uncertainty_mm is not None):
            raise ValueError("selected synthetic quality is inconsistent")
        return OfflineImpactEvidence(
            capture.shot_id, capture.session_id, index, True,
            result.x_mm, result.y_mm,
            result.horizontal_region, result.vertical_region,
            "synthetic impact geometry accepted; physical contact and accuracy unverified",
        )
    return OfflineImpactEvidence(
        capture.shot_id, capture.session_id, None, False,
        None, None, None, None,
        "offline impact withheld: " + (
            temporal.spacing.reason if not temporal.spacing.accepted
            else temporal.selection.reason
        ),
    )
