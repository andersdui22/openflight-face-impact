"""Gates 20-24: offline evidence audit of a bounded frame-candidate batch.

No automatic contact-frame selection or measured accuracy is inferred.
"""

from __future__ import annotations

from dataclasses import dataclass

from .synthetic_frame_candidates import AssessedFrameCandidate
from .synthetic_impact_pipeline import SyntheticImpactStatus


@dataclass(frozen=True)
class SyntheticBatchAudit:
    """Explicit batch outcome counts; never a physical contact declaration."""

    total: int
    accepted_synthetic: int
    rejected_invalid_geometry: int
    rejected_no_tangency: int
    rejected_outside_face: int
    all_rejections_fail_closed: bool
    physical_contact_established: bool = False
    physical_accuracy_established: bool = False


def audit_synthetic_candidate_batch(
    results: tuple[AssessedFrameCandidate, ...],
) -> SyntheticBatchAudit:
    """Validate and summarize a complete bounded offline candidate result set."""
    if not isinstance(results, tuple) or not results:
        raise ValueError("audit requires a nonempty tuple of frame assessments")
    if any(not isinstance(item, AssessedFrameCandidate) for item in results):
        raise ValueError("audit requires frame assessments")
    indices = [item.frame_index for item in results]
    if len(indices) != len(set(indices)):
        raise ValueError("audit frame indices must be distinct")
    counts = {status: 0 for status in SyntheticImpactStatus}
    for item in results:
        result = item.assessment.impact
        quality = item.assessment.quality
        if quality.physically_validated or quality.position_uncertainty_mm is not None:
            raise ValueError("offline audit cannot assert physical validation")
        accepted = result.status is SyntheticImpactStatus.OK
        if quality.accepted_synthetic_geometry != accepted:
            raise ValueError("synthetic quality acceptance contradicts impact status")
        if accepted:
            if result.rejection_reason is not None:
                raise ValueError("accepted result cannot have rejection reason")
        elif (quality.reason != result.rejection_reason
              or any(value is not None for value in (
                  result.x_mm, result.y_mm,
                  result.horizontal_region, result.vertical_region,
              ))):
            raise ValueError("rejection must preserve reason and hide coordinates")
        counts[result.status] += 1
    return SyntheticBatchAudit(
        total=len(results),
        accepted_synthetic=counts[SyntheticImpactStatus.OK],
        rejected_invalid_geometry=counts[SyntheticImpactStatus.INVALID_GEOMETRY],
        rejected_no_tangency=counts[SyntheticImpactStatus.NO_TANGENCY],
        rejected_outside_face=counts[SyntheticImpactStatus.OUTSIDE_FACE],
        all_rejections_fail_closed=True,
    )
